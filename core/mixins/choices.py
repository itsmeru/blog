class StatusChoicesMixin:
    STATUS_CHOICES = [("enabled", "啟用"), ("disabled", "禁用")]


class TradeTypeChoicesMixin:
    TRADE_TYPE_CHOICES = [
        ("telecom", "B.電信模式"),
        ("twd", "C.台幣交易"),
        ("overseas", "D.海外交易"),
        ("points", "E.點數禮包"),
        ("official", "I.官方儲值"),
    ]


class CurrencyChoicesMixin:
    CURRENCY_CHOICES = [
        ("TWD", "台幣"),
        ("CNY", "人民幣"),
        ("USD", "USD"),
        ("POINT", "點數"),
    ]


class ItemTypeChoicesMixin:
    ITEM_TYPE_CHOICES = [
        ("prepaid", "預付"),
        ("service", "服務"),
        ("inventory", "庫存"),
    ]


class TagChoicesMixin:
    TAG_CHOICES = [
        ("uid", "UID"),
        ("api", "API"),
        ("serial", "序號"),
        ("telecom", "電信"),
        ("mycard", "MyCard"),
        ("gash", "Gash"),
        ("jp", "日版"),
        ("global", "國際版"),
        ("mycard_point", "MyCard點卡(點數)"),
        ("cost_gift_card", "有成本禮包幣"),
        ("free_gift_card", "無成本禮包幣"),
    ]


class PaymentMethodChoicesMixin:
    PAYMENT_METHOD_CHOICES = [
        ("esun", "統一金"),
        ("opay", "歐付寶"),
        ("green_card", "綠卡"),
        ("ecpay", "綠界"),
    ]


class MarketTypeChoicesMixin:
    MARKET_TYPE_CHOICES = [
        ("official_partner", "官方合作"),
        ("official_exclusive", "官方獨家"),
        ("manual_topup", "人工儲值"),
        ("auto_topup", "自動儲值"),
        ("points_mall", "點數賣場"),
        ("physical_product", "實體商品"),
        ("dealer_exclusive", "盤商專屬"),
    ]


class StageChoicesMixin:
    STAGE_CHOICES = [
        ("frontstage", "前台"),
        ("backstage", "後台"),
    ]


class DepartmentChoicesMixin:
    DEPARTMENT_CHOICES = [
        ("tech", "技術部"),
        ("sales", "業務部"),
        ("accounting", "會計部"),
        ("operation", "營運部"),
    ]


class CommonChoicesMixin(
    StatusChoicesMixin,
    TradeTypeChoicesMixin,
    CurrencyChoicesMixin,
    ItemTypeChoicesMixin,
    TagChoicesMixin,
    PaymentMethodChoicesMixin,
    MarketTypeChoicesMixin,
    StageChoicesMixin,
):
    pass
