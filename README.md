# Vnmarket - Thư Viện Python Truy Xuất Dữ Liệu Chứng Khoán Việt Nam (Personal Edition)

Bộ công cụ Python client-side gọn nhẹ, an toàn và độc lập để kết nối, chuẩn hoá và phân tích dữ liệu thị trường tài chính Việt Nam (cổ phiếu, chỉ số, phái sinh, chứng quyền, quỹ mở, tỷ giá và vàng).

---

## 🚀 Tính Năng Nổi Bật

- **Hoàn Toàn Độc Lập & An Toàn**: 100% mã nguồn sạch, không chứa script chạy ngầm (auto-run), không thu thập telemetry, không chuyển hướng qua server trung gian.
- **Giao Diện Hợp Nhất (Unified UI)**: Truy cập mọi luồng dữ liệu qua các facade hướng đối tượng trực quan: `Market`, `Reference`, `Fundamental`, `Retail`, `Broker`.
- **Dữ Liệu Chuẩn Hoá**: Dữ liệu trả về đều là pandas DataFrame với tên cột rõ ràng, kiểu dữ liệu số học và timestamp chuẩn.
- **Đa Dạng Nguồn Dữ Liệu**: Tích hợp các kết nối công khai từ KBS, VCI, MSN, FMarket với cơ chế client-side rate limiting, tự động retry (`tenacity`) và ngắt mạch (`circuit breaker`).

---

## 📦 Cài Đặt

### 1. Cài đặt vào dự án khác qua Git Release Tag (Khuyên dùng)

```bash
# Cài đặt phiên bản phát hành v1.0.1 qua pip
pip install "git+https://github.com/baby-hero-404/vnmarket.git@v1.0.1"

# Hoặc sử dụng uv (cực nhanh)
uv add "vnmarket @ git+https://github.com/baby-hero-404/vnmarket.git@v1.0.1"
```

Thêm vào `requirements.txt` của dự án khác:
```text
vnmarket @ git+https://github.com/baby-hero-404/vnmarket.git@v1.0.1
```

### 2. Cài đặt phát triển cục bộ (Local Development)

```bash
git clone https://github.com/baby-hero-404/vnmarket.git
cd vnmarket

# Cài đặt ở chế độ editable với đầy đủ công cụ dev/test
make install-dev
```

---

## 💡 Hướng Dẫn Sử Dụng (Quickstart)

### 1. Giao Diện Hợp Nhất (Unified UI Facade)

```python
from vnmarket import Fundamental, Market, Reference

market = Market()
ref = Reference()
fa = Fundamental()

# 1. Lấy dữ liệu lịch sử giá cổ phiếu hoặc chỉ số (OHLCV)
df_quote = market.equity.ohlcv("SSI", start="2024-01-01", end="2024-12-31")
print(df_quote.head())

# 2. Lấy danh sách toàn bộ cổ phiếu và sàn niêm yết
df_symbols = ref.equity.list(source="KBS")
print(df_symbols.head())

# 3. Xem thông tin hồ sơ doanh nghiệp & cơ cấu cổ đông
df_profile = ref.company("FPT").info()
df_holders = ref.company("FPT").shareholders()
print(df_profile)

# 4. Báo cáo tài chính (Bảng cân đối kế toán, Kết quả KD)
df_balance = fa.equity("TCB").balance_sheet(period="quarter")
df_income = fa.equity("TCB").income_statement(period="quarter")
print(df_balance.head())
```

### 2. Sử Dụng Lớp Trực Tiếp (Direct Class API)

```python
from vnmarket import Company, Finance, Listing, Quote

# 1. Lịch sử giá
quote = Quote(symbol="HPG")
df_history = quote.history(start="2024-01-01", end="2024-06-01")

# 2. Tra cứu niêm yết
listing = Listing()
df_all = listing.all_symbols()

# 3. Chỉ số tài chính & Báo cáo
finance = Finance(symbol="VNM")
df_ratios = finance.ratios()
```

### 3. Khám Phá & Tra Cứu API Tự Động (`show_api`)

Bạn có thể tra cứu toàn bộ danh mục hàm và tham số được hỗ trợ ngay trong terminal hoặc Jupyter Notebook:

```python
from vnmarket import show_api

# Liệt kê tất cả các phương thức hỗ trợ trong giao diện Unified UI
show_api()
```

---

## 📊 Bản Đồ Danh Mục Dữ Liệu

| Phân Loại | Domain UI | Các Phương Thức Chính |
|---|---|---|
| **Cổ phiếu (Equity)** | `market.equity`, `fa.equity`, `ref.company` | `ohlcv()`, `quote()`, `trades()`, `balance_sheet()`, `income_statement()`, `cash_flow()`, `ratios()`, `info()`, `shareholders()`, `officers()`, `subsidiaries()` |
| **Chỉ số (Index)** | `market.index`, `ref.index` | `ohlcv()`, `list()`, `members()`, `groups()`, `info()` |
| **Phái sinh & Chứng quyền** | `market.futures`, `market.warrant`, `ref.futures`, `ref.warrant` | `ohlcv()`, `quote()`, `trades()`, `list()`, `info()` |
| **Phân loại ngành** | `ref.industry` | `list()`, `sectors()` |
| **Quỹ mở (Mutual Funds)** | `market.fund`, `ref.fund` | `nav()`, `history()`, `top_holding()`, `industry_holding()`, `asset_holding()`, `list()` |
| **Tỷ giá & Kim loại quý** | `market.forex`, `retail.gold` | `exchange_rate()`, `gold_price()` |

---

## 🛠️ Lệnh Phát Triển (Makefile Automation)

Dự án tích hợp sẵn `Makefile` chuẩn hóa:

```bash
make help        # Xem toàn bộ danh sách lệnh và hướng dẫn
make verify      # Chạy format, lint và toàn bộ 700+ bài test
make format      # Tự động format mã nguồn với Ruff
make lint        # Kiểm tra linter
make test        # Chạy test suite
make test-live   # Chạy test kết nối live endpoint (cần internet)
make build       # Đóng gói sdist và wheel vào thư mục dist/
make tag         # Xem version hiện tại và gợi ý lệnh tag release
```

---

## 📄 Giấy Phép (License)

Phát hành dưới giấy phép [MIT License](LICENSE.md). Tự do sử dụng và mở rộng cho mục đích cá nhân và nghiên cứu.
