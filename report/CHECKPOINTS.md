# Nhật ký checkpoint

Thực hiện theo README.md, GUIDE.md, RUBRIC.md và các tài liệu guides/pseudocode/.

| Phần | Điều kiện hoàn thành | Trạng thái |
|---|---|---|
| 0.2 | Bộ test được cung cấp đạt; kết nối mô hình trả OK | Đạt: 12 passed trên Windows; OpenRouter trả OK |
| 0.3 | Chạy tour, ghi công cụ và quy tắc ngữ cảnh vào báo cáo | Tour đạt; có 9 công cụ và system prompt mặc định rỗng |
| 1.1 | Định nghĩa ít nhất hai subagent hợp lệ | Đạt test cấu trúc; có explorer, implementer, reviewer |
| 1.2 | Backend và agent đạt test_02 trên Linux | Đạt: 9/9 test |
| 1.3 | Runner đạt test_03; baseline data-learn có bản ghi thật | Đạt: 6/6 test; data-learn 5/8, 29.220 token, không có lỗi |
| 2 | Baseline và subagents đủ ba tác vụ học; phân loại lỗi | Đạt: mỗi điều kiện 18/18 kỹ thuật, 0/9 quy ước; phân loại 9 lỗi E trong báo cáo |
| 3 | Curator đạt test_04, sinh skill hợp lệ; chạy thử skills-auto | Đạt: 2/2 test; 3 skill do mô hình sinh; dev 10/10, 8/8, 9/9, skills_read=1 mỗi tác vụ |
| 4.0–4.1 | Commit hypotheses trước tag freeze | Chưa thực hiện |
| 4.2–4.4 | Đủ kết quả chính thức; verify_freeze OK; bảng và thống kê | Chưa thực hiện |
| 5 | Báo cáo đủ mục, số liệu khớp bản ghi và vết | Chưa thực hiện |

## Ghi chú môi trường

- Môi trường Windows có Deep Agents 0.7.21; pytest ban đầu gặp quyền truy cập thư mục tạm trong sandbox. Chạy lại ngoài sandbox đạt 12/12 test.
- GUIDE yêu cầu Linux vì LocalShellBackend dùng /bin/sh. Sử dụng Ubuntu WSL và Python 3.14.4. Sau thử môi trường `.venv/wsl` trên ổ Windows (cài và chạy chậm), môi trường chạy chính được đặt tại `/root/.local/share/lab-k4-day20-venv` trên hệ thống tệp Linux.
- Ubuntu thiếu ensurepip. Pip được bootstrap từ https://bootstrap.pypa.io/get-pip.py; thư viện cài đúng pyproject.toml.
- Môi trường đầu tiên ở /tmp bị WSL dọn giữa các phiên; chuyển sang `.venv/wsl` để giữ môi trường. Đây là lỗi hạ tầng, không dùng làm bằng chứng lỗi tác tử.
- Không mở check.py hoặc kết quả đánh giá để thiết kế skill trước khi đóng băng. Không sửa tests/, tasks/, scripts/ hoặc phần mã được cung cấp.
- Full suite: 29 passed; đầu ra lưu tại `pytest.txt`.
- Lỗi CRLF của fixture code-learn được xác nhận bằng SHA-256: bản chuẩn hóa LF bằng bản trong git và hash trong checker. Chỉ chuẩn hóa bản sao `.py` trong sandbox. Bản chạy đầu lưu tại results/baseline-crlf; không dùng làm phản hồi curator.
