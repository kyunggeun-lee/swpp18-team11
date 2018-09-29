import datetime

from .ticket import TicketService
from ..models import Purchasable, PurchasableOption, Store, TxLog, Tx, TxItem, TxItemOption, TxCredit
from decimal import Decimal
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import List, Type, Dict, Optional, ContextManager, Union

@dataclass
class PurchasableOptionSpec:
    purchasable_option: PurchasableOption
    qty: int

    @property
    def total_price(self):
        return self.purchasable_option.base_price * self.qty


@dataclass
class PurchasableSpec:
    purchasable: Purchasable
    qty: int
    purchasable_option_specs: List[PurchasableOptionSpec] = field(default_factory=list)

    def add_option(self, purchasable_option: PurchasableOption, qty: int) -> PurchasableOptionSpec:
        purchasable_option_spec = PurchasableOptionSpec(purchasable_option, qty)
        self.purchasable_option_specs.append(purchasable_option_spec)
        return purchasable_option_spec

    @property
    def total_price(self):
        return sum(spec.total_price for spec in self.purchasable_option_specs)

@dataclass
class OrderSpec:
    store: Store
    purchasable_specs: List[PurchasableSpec] = field(default_factory=list)

    def add_purchasable(self, purchasable: PurchasableSpec, qty: int) -> PurchasableSpec:
        purchasable_spec = PurchasableSpec(purchasable, qty)
        self.purchasable_specs.append(purchasable_spec)
        return purchasable_spec

    @property
    def total_price(self):
        return sum(spec.total_price for spec in self.purchasable_specs)


@dataclass
class OrderTx:
    utxid: str
    _tx_log: TxLog
    purchase_method: Optional["PurchaseMethod"] = None
    _tx: Optional[Tx] = None

    @property
    def state(self):
        return self._tx_log.state

    @property
    def tx(self):
        return self._tx



@dataclass
class OrderCreditor:
    order_tx: OrderTx
    def credit_order(self, *,
                     amount: Union[str, int, Decimal],
                     name: str,
                     ref: str,
                     bank: str,
                     value_date: Optional[datetime.date] = None):
        value_date = value_date or datetime.date.today()
        decimal_amount = Decimal(amount)
        credit = TxCredit(
            tx=self.order_tx._tx,
            amount=decimal_amount,
            customer_name=name,
            customer_ref=ref,
            customer_bank=bank,
            value_date=value_date,
        )
        credit.save()


@dataclass
class TxService:
    ticket_service: TicketService = field(default_factory=TicketService)

    def prepare_order(self, *,
                      utxid: str,
                      order_spec: OrderSpec,
                      part_ref: str = "") -> OrderTx:
        tx_log = TxLog(
            utxid=utxid,
            store=order_spec.store,
            total_price=order_spec.total_price,
            extra_props="{}",
            part_ref=part_ref,
        )
        tx_log.save()
        for spec in order_spec.purchasable_specs:
            self._itemify_purchasable_spec(spec, tx_log)

        return OrderTx(utxid=utxid, _tx_log=tx_log)

    def load(self, utxid: str) -> OrderTx:
        tx = Tx.objects.filter(utxid=utxid).first()
        tx_log = TxLog.objects.filter(utxid=utxid).first()

        tx_like = tx or tx_log

        purchase_method = None
        if tx_like and tx_like.purchase_type:
            cls = PurchaseMethod.get(tx_like.purchase_type)
            purchase_method = cls.load(tx_like.purchase_data)

        return OrderTx(
            utxid=utxid,
            _tx_log=tx_log,
            _tx=tx,
            purchase_method=purchase_method,
        )

    def save(self, order_tx: OrderTx):
        purchase_method = order_tx.purchase_method
        if purchase_method:
            purchase_type_name = PurchaseMethod.get_name_of(purchase_method.__class__)
            purchase_data = purchase_method.dump()
            tx_likes = [order_tx._tx, order_tx._tx_log]
            for tx_like in tx_likes:
                if not tx_like:
                    continue
                tx_like.purchase_type = purchase_type_name
                tx_like.purchase_data = purchase_data
                tx_like.save()

    def start_order(self, order_tx: OrderTx, purchase_method: "PurchaseMethod"):
        order_tx.purchase_method = purchase_method
        order_tx._tx_log.state = 'pending'
        self.save(order_tx)

    @contextmanager
    def finish_order(self, order_tx: OrderTx) -> ContextManager[OrderCreditor]:
        tx = Tx()
        order_tx._tx_log.state = 'done'
        order_tx._tx_log.assign_to(tx)
        tx.save()
        tx.txitem_set.set(order_tx._tx_log.txitem_set.all())

        order_tx._tx = tx

        yield OrderCreditor(order_tx)

        self._after_finished(order_tx)

    def _after_finished(self, order_tx):
        store = order_tx._tx.store
        self.ticket_service.convert_order_tx(order_tx, store)

    def _itemify_purchasable_spec(self, purchasable_spec: PurchasableSpec, tx_log):
        purchasable = purchasable_spec.purchasable
        tx_item = TxItem(
            tx_log=tx_log,
            purchasable=purchasable_spec.purchasable,
            purchasable_base_price=purchasable.base_price,
            qty=purchasable_spec.qty,
            price=purchasable.base_price,
            total_price=purchasable_spec.total_price,
        )
        tx_item.save()
        for spec in purchasable_spec.purchasable_option_specs:
            self._itemify_purchasable_option_spec(spec, tx_item)
        return tx_item

    def _itemify_purchasable_option_spec(self, purchasable_option_spec: PurchasableOptionSpec, tx_item):
        tx_item_option = TxItemOption(
            tx_item=tx_item,
            purchasable_option=purchasable_option_spec.purchasable_option,
            base_price=purchasable_option_spec.purchasable_option.base_price,
            qty=purchasable_option_spec.qty,
            total_price=purchasable_option_spec.total_price,
        )
        tx_item_option.save()
        return tx_item_option



PurchaseMethodClass = Type["PurchaseMethod"]

class PurchaseMethod:
    name_mapping: Dict[str, PurchaseMethodClass] = {}
    name: str = None

    @classmethod
    def load(cls, data: str) -> "PurchaseMethod":
        return cls()

    def dump(self) -> str:
        return ""

    @classmethod
    def register_as(cls, type_name: str):
        if type_name == '':
            raise ValueError("type name cannot be an empty string")
        cls.name_mapping[type_name] = cls

    @classmethod
    def get(cls, type_name: str) -> Optional[PurchaseMethodClass]:
        return cls.name_mapping.get(type_name)

    @classmethod
    def get_name_of(cls, type: PurchaseMethodClass) -> Optional[str]:
        for name, target_type in cls.name_mapping.items():
            if type == target_type:
                return name
        return None
