# TÀI LIỆU SPECIFICATION (SPEC) - EXEC LAUNCHER

**Mã dự án:** EXL-001  
**Phiên bản SPEC:** 1.0  
**Nền tảng mục tiêu:** Debian 13 / Linux Desktop (GNOME/GTK compatible)  
**Đối tượng áp dụng:** Code Agent / Development Team  

---

## 1. GIỚI THIỆU (INTRODUCTION)

### 1.1. Mục đích
Xây dựng một ứng dụng GUI nhẹ nhàng (lightweight) cho phép người dùng quản lý, cấu hình và thực thi các script hệ thống thông qua các profile được định nghĩa trước. Ứng dụng đóng vai trò là lớp trung gian (launcher) giữa người dùng và các tác vụ dòng lệnh.

### 1.2. Phạm vi (Scope)
- **Trong phạm vi:** Quản lý cấu hình profile, thực thi script trong terminal riêng, thông báo trạng thái, tích hợp vào menu hệ thống.
- **Ngoài phạm vi:** chỉnh sửa script nội bộ, giám sát tiến trình chi tiết (monitoring), lập lịch trình (scheduling).

---

## 2. YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)

### 2.1. Quản lý Profile (Profile Management)
- **FR-01:** Hệ thống phải tự động quét và tải danh sách profile từ thư mục cấu hình khi khởi động.
- **FR-02:** Hệ thống phải hỗ trợ tải lại (reload) danh sách profile mà không cần khởi động lại ứng dụng.
- **FR-03:** Mỗi profile phải được định nghĩa bằng một file cấu hình riêng biệt.
- **FR-04:** Hệ thống phải bỏ qua các file cấu hình không hợp lệ và ghi nhận lỗi (log/toast) mà không làm crash ứng dụng.

### 2.2. Thực thi Script (Script Execution)
- **FR-05:** Khi người dùng chọn một profile và kích hoạt lệnh chạy, hệ thống phải mở một cửa sổ terminal riêng biệt để hiển thị output của script.
- **FR-06:** Việc thực thi script phải diễn ra trên một luồng xử lý riêng (background thread/process), không được làm đóng băng giao diện người dùng (UI blocking).
- **FR-07:** Hệ thống phải hỗ trợ chạy nhiều profile đồng thời (concurrent execution).
- **FR-08:** Hệ thống phải hỗ trợ chế độ đặc quyền (sudo) dựa trên cấu hình của từng profile.

### 2.3. Cấu hình (Configuration)
- **FR-09:** Người dùng phải có thể truy cập nhanh vào thư mục chứa file cấu hình để chỉnh sửa thủ công bằng editor bên ngoài.
- **FR-10:** Hệ thống phải cung cấp cơ chế tạo file mẫu (template) để người dùng biết cấu trúc cấu hình.

### 2.4. Thông báo (Notification)
- **FR-11:** Hệ thống phải hiển thị thông báo ngắn hạn (toast) ngay trên giao diện ứng dụng khi có sự kiện (thành công, lỗi, thông tin).
- **FR-12:** Hệ thống phải gửi thông báo đến hệ thống điều hành (System Notification) song song với toast.

---

## 3. YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS)

### 3.1. Hiệu năng (Performance)
- **NFR-01:** Thời gian khởi động ứng dụng phải dưới 2 giây trên phần cứng tiêu chuẩn.
- **NFR-02:** Ứng dụng phải tiêu thụ tài nguyên hệ thống ở mức thấp (ưu tiên nhẹ nhàng).
- **NFR-03:** Giao diện phải phản hồi ngay lập tức khi người dùng thao tác (click, chọn), bất kể trạng thái script đang chạy.

### 3.2. Tương thích (Compatibility)
- **NFR-04:** Ứng dụng phải tuân theo chuẩn **XDG Base Directory Specification** cho việc lưu trữ cấu hình và dữ liệu.
- **NFR-05:** Ứng dụng phải tương thích với môi trường desktop sử dụng GTK4 (ưu tiên Debian 13 default).
- **NFR-06:** Ứng dụng phải tự động phát hiện hoặc cho phép cấu hình terminal emulator mặc định của hệ thống.

### 3.3. Bảo mật (Security)
- **NFR-07:** Ứng dụng không được lưu trữ mật khẩu hay thông tin nhạy cảm trong file cấu hình.
- **NFR-08:** Khi chế độ sudo được kích hoạt, việc xác thực phải do terminal hệ thống xử lý (không hard-code password).

### 3.4. Khả năng sử dụng (Usability)
- **NFR-09:** Giao diện phải tối giản, tập trung vào chức năng chính (Chọn -> Chạy).
- **NFR-10:** Thông báo lỗi phải rõ ràng, chỉ dẫn được nguyên nhân (ví dụ: không tìm thấy file script).

---

## 4. SPECIFICATION DỮ LIỆU (DATA SPECIFICATION)

### 4.1. Định dạng Cấu hình (Configuration Format)
- **Định dạng:** YAML (YAML Ain't Markup Language).
- **Mã hóa:** UTF-8.
- **Vị trí lưu trữ:** Thư mục cấu hình người dùng (User Config Directory) theo chuẩn XDG.
- **Cấu trúc file:** Mỗi file YAML đại diện cho một Profile duy nhất.

### 4.2. Schema Profile (Profile Schema)
File cấu hình profile phải tuân thủ các trường dữ liệu sau:

| Trường (Field) | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `name` | String | **Có** | Tên hiển thị của profile trên giao diện. |
| `script` | String (Path) | **Có** | Đường dẫn tuyệt đối hoặc tương đối đến file thực thi. |
| `sudo_mode` | Integer (0/1) | Không | Mặc định là 0. Nếu là 1, script sẽ được gọi kèm quyền sudo. |
| `work_dir` | String (Path) | Không | Thư mục làm việc hiện hành khi chạy script. |
| `args` | List[String] | Không | Danh sách các tham số truyền vào script. |
| `terminal` | String | Không | Chỉ định tên terminal emulator (nếu để trống sẽ dùng mặc định hệ thống). |

### 4.3. Ví dụ Dữ liệu hợp lệ
```yaml
name: "System Update"
script: "/usr/bin/apt"
sudo_mode: 1
args:
  - "update"
  - "-y"
```

---

## 5. SPECIFICATION GIAO DIỆN (UI SPECIFICATION)

### 5.1. Bố cục chính (Main Layout)
Giao diện chính phải bao gồm các thành phần logic sau:
1.  **Khu vực chọn Profile:** Một danh sách xổ xuống (Dropdown/Combo box) hiển thị trường `name` từ các file cấu hình.
2.  **Khu vực hành động chính:** Nút lệnh để kích chạy profile đang chọn.
3.  **Khu vực điều khiển phụ:** Các nút lệnh để tải lại danh sách, mở thư mục cấu hình, tạo mẫu.
4.  **Khu vực thông báo:** Vùng hiển thị toast message (thường nằm ở cạnh hoặc đáy cửa sổ).

### 5.2. Luồng tương tác (Interaction Flow)
1.  **Khởi động:** Ứng dụng đọc thư mục cấu hình -> Populate danh sách chọn.
2.  **Chọn Profile:** Người dùng chọn một mục trong danh sách.
3.  **Thực thi:** Người dùng nhấn nút chạy -> Ứng dụng xác thực đường dẫn script -> Spawn process terminal -> Trả quyền điều khiển về UI ngay lập tức.
4.  **Phản hồi:** Nếu thành công -> Hiển thị Toast "Đã chạy". Nếu lỗi (không tìm thấy file) -> Hiển thị Toast "Lỗi".
5.  **Cập nhật:** Người dùng sửa file YAML bên ngoài -> Nhấn nút Reload -> Ứng dụng đọc lại thư mục -> Cập nhật danh sách chọn.

### 5.3. Trạng thái (State Management)
- **Trạng thái Idle:** Sẵn sàng chọn và chạy.
- **Trạng thái Running:** Vẫn cho phép chọn profile khác và chạy tiếp (không disable UI).
- **Trạng thái Error:** Hiển thị thông báo lỗi nhưng không khóa ứng dụng.

---

## 6. SPECIFICATION TÍCH HỢP HỆ THỐNG (SYSTEM INTEGRATION)

### 6.1. Desktop Entry
- Ứng dụng phải cung cấp file `.desktop` để xuất hiện trong Menu Applications của hệ điều hành.
- File `.desktop` phải cấu hình `Terminal=false` (ứng dụng tự quản lý terminal con).
- Icon ứng dụng phải sử dụng icon chuẩn hệ thống (ví dụ: `utilities-terminal`).

### 6.2. Process Management
- Ứng dụng cha (Launcher) không được chờ (wait) tiến trình con (Script).
- Tiến trình con phải độc lập, việc đóng ứng dụng cha không được tắt đột ngột tiến trình con đang chạy (daemonize hoặc detach process).

### 6.3. Dependency Management
- Ứng dụng phải kiểm tra sự tồn tại của các thư viện đồ họa và xử lý YAML trước khi khởi tạo giao diện.
- Nếu thiếu thư viện, phải thông báo lỗi rõ ràng cho người dùng qua terminal hoặc log.

---

## 7. XỬ LÝ LỖI VÀ BIÊN (ERROR HANDLING & EDGE CASES)

| Tình huống | Hành vi hệ thống yêu cầu |
| :--- | :--- |
| **Thư mục config trống** | Hiển thị danh sách rỗng, không crash. Có thể gợi ý tạo mẫu. |
| **File YAML sai cú pháp** | Bỏ qua file đó, ghi log lỗi, tiếp tục tải các file còn lại. |
| **Script không tồn tại** | Khi bấm Run: Hiển thị Toast lỗi, không mở terminal. |
| **Script không có quyền exec** | Khi bấm Run: Hiển thị Toast cảnh báo quyền truy cập. |
| **Terminal emulator không tìm thấy** | Fallback về `gnome-terminal` hoặc báo lỗi không thể thực thi. |
| **Người dùng đóng app khi script đang chạy** | Script vẫn tiếp tục chạy độc lập (do đã tách process). |

---

## 8. TIÊU CHÍ CHẤP NHẬN (ACCEPTANCE CRITERIA)

Để được coi là hoàn thành, ứng dụng phải vượt qua các kiểm tra sau:
1.  **AC-01:** Cài đặt thành công trên Debian 13 sạch, xuất hiện icon trong Menu.
2.  **AC-02:** Tạo được file profile YAML mới, Reload app thấy tên profile xuất hiện trong dropdown.
3.  **AC-03:** Bấm Run profile thường -> Mở terminal -> Script chạy -> Output hiển thị.
4.  **AC-04:** Bấm Run profile sudo -> Mở terminal -> Yêu cầu password -> Script chạy.
5.  **AC-05:** Chạy cùng lúc 3 profile -> Mở 3 terminal riêng biệt -> UI không bị đơ.
6.  **AC-06:** Xóa file YAML khi app đang chạy -> Reload -> Tên profile biến mất khỏi dropdown.
7.  **AC-07:** Sửa sai cú pháp YAML -> Reload -> App không crash, chỉ bỏ qua file lỗi.

---

**KẾT THÚC TÀI LIỆU SPECIFICATION**