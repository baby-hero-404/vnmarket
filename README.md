# Vnmarket - Thư Viện Python Truy Xuất Dữ Liệu Chứng Khoán Việt Nam (Personal Edition)

Bộ công cụ Python client-side gọn nhẹ, an toàn và độc lập để kết nối, chuẩn hoá và phân tích dữ liệu thị trường tài chính Việt Nam (cổ phiếu, chỉ số, phái sinh, chứng quyền, quỹ mở).

---

## Tính Năng Nổi Bật

- **Hoàn Toàn Độc Lập & An Toàn**: Không chứa script chạy ngầm (auto-run), không gọi telemetry, không phụ thuộc vào server trung gian hay các gói độc quyền.
- **Giao Diện Hợp Nhất (Unified UI)**: Truy cập mọi nhóm dữ liệu qua các domain object trực quan: `Market`, `Reference`, `Fundamental`, `Retail`.
- **Dữ Liệu Chuẩn Hoá**: Tất cả dữ liệu trả về đều là pandas DataFrame với tên cột rõ ràng, kiểu dữ liệu chuẩn hoá và timestamp chính xác.
- **Đa Dạng Nguồn Dữ Liệu**: Tích hợp các kết nối công khai từ KBS, VCI, MSN, FMarket với cơ chế tự động thử lại (tenacity retry), rate limiting và bảo vệ ngắt mạch (circuit breaker) tại client.

---

## Cài Đặt

Cài đặt các gói phụ thuộc tiêu chuẩn:

```bash
pip install -r requirements.txt
```

Hoặc cài đặt trực tiếp thư viện ở chế độ editable (dành cho phát triển cá nhân):

```bash
pip install -e .
```

---

## Hướng Dẫn Sử Dụng Nhanh

### 1. Giao Diện Hợp Nhất (Unified UI)

```python
from vnmarket import Fundamental, Market, Reference

market = Market()
ref = Reference()
fa = Fundamental()

# 1. Lấy dữ liệu lịch sử giá chỉ số thị trường (OHLCV)
df_index = market.index("VNINDEX").ohlcv(start="2024-01-01", end="2024-05-01")
print(df_index.head())

# 2. Lấy thông tin hồ sơ doanh nghiệp
df_profile = ref.company("FPT").info()
print(df_profile)

# 3. Lấy báo cáo tài chính (Bảng cân đối kế toán) theo quý / năm
df_balance = fa.equity("TCB").balance_sheet(period="quarter")
print(df_balance.head())

# 4. Lấy danh sách cổ phiếu theo sàn hoặc nhóm chỉ số
df_symbols = ref.equity.list(source="KBS")
print(df_symbols.head())
```

### 2. Sử Dụng Lớp Trực Tiếp (Direct Class API)

```python
from vnmarket import Quote, Company, Finance, Listing

# Lịch sử giá
quote = Quote(symbol="HPG")
df_quote = quote.history(start="2024-01-01", end="2024-04-01")

# Thông tin niêm yết
listing = Listing()
df_all = listing.all_symbols()

# Báo cáo tài chính
finance = Finance(symbol="VNM")
df_income = finance.income_statement(period="year")
```

---

## Cấu Trúc Các Nhóm Dữ Liệu

| Nhóm | Domain UI | Các Phương Thức Tiêu Biểu |
|---|---|---|
| **Cổ phiếu (Equity)** | `market.equity`, `fa.equity`, `ref.company` | `ohlcv()`, `quote()`, `trades()`, `balance_sheet()`, `income_statement()`, `cash_flow()`, `ratios()`, `info()`, `shareholders()`, `officers()`, `subsidiaries()` |
| **Chỉ số (Index)** | `market.index`, `ref.index` | `ohlcv()`, `list()`, `members()`, `groups()`, `info()` |
| **Phái sinh & Chứng quyền** | `market.futures`, `market.warrant`, `ref.futures`, `ref.warrant` | `ohlcv()`, `quote()`, `trades()`, `list()`, `info()` |
| **Phân loại ngành** | `ref.industry` | `list()`, `sectors()` |
| **Quỹ đầu tư (Funds)** | `market.fund`, `ref.fund` | `nav()`, `history()`, `top_holding()`, `industry_holding()`, `asset_holding()`, `list()` |
| **Vĩ mô & Hàng hóa** | `market.forex`, `market.commodity`, `market.crypto`, `retail` | `ohlcv()`, `exchange_rate()` |

---

## Kiểm Tra & Phát Triển

Chạy bộ kiểm thử tự động:

```bash
# Chạy toàn bộ test
pytest

# Kiểm tra code style và formatting với Ruff
ruff check .
ruff format .
```

---

## Giấy Phép (License)

Mã nguồn được phân phối theo giấy phép [MIT](LICENSE.md).
