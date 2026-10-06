# Báo cáo Lab: Self evolving Agentic

Ngày thực hiện: 06/10/2026 (Asia/Saigon). Bản ghi thời gian của runner dùng UTC.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| NguyenThiLeNa (theo tên kho) | 2A202602501 | Thực hiện lab với hỗ trợ AI: harness, thí nghiệm, phân tích và báo cáo |

- Mô hình: `openai/gpt-6-luna` qua OpenRouter (`https://openrouter.ai/api/v1`), `LAB_TEMPERATURE=0`, `recursion_limit=60`.
- Deep Agents: `0.7.21`; Ubuntu WSL trên Windows; Python Linux `3.14.4`. Môi trường chạy chính: `/root/.local/share/lab-k4-day20-venv`; không dùng Docker. Phiên bản phụ thuộc được lưu trong `requirements-freeze.txt`.
- Đến lúc đóng băng: 9 lần chạy hợp lệ trên tập học và 1 lần chạy lại do CRLF; curator chạy 1 lần, kiểm tra kết nối 1 lần. Tài liệu hiện tại không nêu ngân sách số lần chạy cụ thể.
- Commit của tag `freeze`: điền sau khi tạo tag; H1–H3 được commit trước tag.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Điểm đánh giá trung bình của subagents sẽ tương đương baseline, còn token cao hơn. Trên tập học hai điều kiện đều đạt 18/18 check kỹ thuật nhưng 0/9 check quy ước; chia việc không cung cấp tri thức Acme còn thiếu. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) ghi nhận chi phí token tăng trong hệ thống đa tác tử; mức 15× của họ so với chat thường không phải hệ số áp dụng cho lab này.
- H2 (skills-auto so với baseline): Skills-auto sẽ có điểm đánh giá trung bình cao nhất trong ba điều kiện nhờ chuyển các quy ước Acme đã học sang tác vụ mới cùng loại; lợi ích chủ yếu ở check quy ước. Đây là dự đoán từ phản hồi cụ thể của lab. [SkillsBench](https://arxiv.org/abs/2602.12670) cho thấy hiệu quả skill phụ thuộc ngữ cảnh và skill tự sinh không luôn có lợi, nên không coi định dạng hợp lệ là bằng chứng hiệu quả.
- H3 (tác vụ học so với tác vụ đánh giá): Mức cải thiện của skills-auto so với baseline trên tập học sẽ lớn hơn trên tập đánh giá, vì các quy ước mới chưa có phản hồi để học. [SkillEvolBench](https://skillevolbench.github.io/) ghi nhận cải thiện ở acquisition/replay không đảm bảo chuyển giao ổn định sang deployment. Chênh lệch còn có thể do độ khó và nhiễu; không tự động kết luận quá khớp chỉ từ một lần chạy.

Các dự đoán này được viết sau phản hồi tập học và trước khi chạy hoặc xem điểm đánh giá; commit `hypotheses` phải đứng trước `freeze`.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tour thực tế thấy chín công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy lệnh shell. Kết quả gốc được lưu trong `tour.txt`.
2. `general-purpose` là subagent mặc định cho nghiên cứu, tìm tệp/nội dung và công việc nhiều bước; có cùng bộ công cụ với tác tử chính. Mỗi lần gọi mặc định không giữ trạng thái; chỉ nhận prompt giao việc và trả một báo cáo cuối. Vì vậy phải truyền đủ yêu cầu và đường dẫn, rồi tự kiểm tra kết quả.
3. System prompt mặc định trong tour là chuỗi rỗng. Chỉ dẫn hành vi từ `task`: “Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report.” Chỉ dẫn từ `execute`: “You MUST avoid using search commands like find and grep.” Mô tả công cụ vì thế cũng cung cấp chỉ dẫn hành vi. Trong thí nghiệm, harness dùng nguyên `BASE_PROMPT` được cung cấp.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | rule_type_hints | E | `RULE: every public function ... has type annotations on all parameters and on the return value.` |
| code-learn | rule_regression_tests | E | `RULE: add tests/test_regressions.py ... (at least 3); the file must pass.` |
| code-learn | rule_changelog | E | `RULE: record each fix in CHANGELOG.md under ... '## Unreleased' ... (at least 3 bullets).` |
| data-learn | rule_money_in_cents | E | `RULE: money values in answer.json are integer cents`. |
| data-learn | rule_meta_block | E | `RULE: answer.json has an object meta` với source, rows_in, rows_used. |
| data-learn | rule_clean_csv | E | `RULE: write workspace/clean.csv` với order_id,timestamp_utc,region,amount_cents. |
| logs-learn | rule_service_names | E | `RULE: service names ... lower-case with '-' replaced by '_'`. |
| logs-learn | rule_sorted_errors | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| logs-learn | rule_schema_header | E | `RULE: ... schema_version: 2` và `generated_by: log-triage`. |

Bằng chứng gốc: `../results/baseline/<task>/run.json` và `trace.md`. Cả 9/9 lỗi hợp lệ thuộc E: quy ước tổ chức chỉ lộ qua review-bot feedback. Skill có thể giữ các quy ước này cho tác vụ cùng miền.

Bằng chứng phủ định: baseline đạt 18/18 check kỹ thuật (code 7/7, data 5/5, logs 6/6). Trace cho thấy tác tử đọc README và source/docstring (A), code chạy lại bộ test 6 passed (B), sửa hàm dùng chung và đạt other_caller_fixed (C), xử lý dữ liệu bẩn, múi giờ, traceback và repeat_count đúng (D). Các tệp mà câu trả lời cuối tuyên bố đã tạo đều được bộ chấm đọc thành công; không có bằng chứng check thất bại thuộc F. Những quan sát này không chứng minh mọi hành vi đều hoàn hảo, nhưng không hỗ trợ quy lỗi kỹ thuật cho chín check trên.

Lần code-learn đầu có lỗi tests_not_modified do checkout CRLF trong khi bộ chấm dùng hash LF; không phải tác tử sửa test. Hash sau chuẩn hóa LF khớp byte với `git show HEAD:<path>`. Runner chỉ chuẩn hóa `.py` trong bản sao sandbox; tệp gốc không đổi. Kết quả đầu (6/10, 78.480 token) lưu tại `../results/baseline-crlf/code-learn`; chạy lại đạt 7/10. Kết quả hạ tầng này không đưa vào bảng chính hoặc prompt curator.

## 5. Điều kiện `subagents` (Phần 2.3)

Ba subagent tự định nghĩa: explorer đọc tài liệu/dữ liệu và báo cáo, implementer thực hiện thay đổi, reviewer kiểm tra độc lập. Description nêu khi nào gọi; system prompt quy định phạm vi và ngữ cảnh chỉ từ lời giao việc. Harness nối PATHS_NOTE cho từng subagent. General-purpose mặc định vẫn tồn tại.

| Tác vụ học | Subagent được gọi | subagent_calls | Token baseline | Token subagents | Giây baseline / subagents |
|---|---|---:|---:|---:|---:|
| code-learn | explorer, implementer | 2 | 57.195 | 104.888 | 62,6 / 132,0 |
| data-learn | explorer | 1 | 29.220 | 45.593 | 28,8 / 48,8 |
| logs-learn | general-purpose | 1 | 28.069 | 87.867 | 28,6 / 80,3 |

Reviewer không được gọi trên tập học. Token trung bình tăng từ 38.161 lên 79.449 (2,08×), điểm trung bình đều 0,664. Token đo đủ các lời gọi LLM nhờ callback; số lần gọi công cụ chỉ đếm luồng chính.

Vết code cho thấy tác tử chính đọc lại source sau implementer, chạy test ban đầu sai thư mục rồi sửa bằng `cd workspace`; cuối cùng 6 passed và các assert bổ sung đạt. Lời giao việc implementer truyền yêu cầu docstring nhưng cấm mọi sửa đổi trong tests/, rộng hơn yêu cầu chỉ bảo vệ test gốc; điều này cũng không khuyến khích thêm regression test. Lời giao explorer cho data thiếu các trường cần tính và ranh giới thời gian; subagent vì thế báo thiếu thông tin xử lý amount dù đề chính đã quy định. Tác tử chính vẫn tính theo đề gốc và đạt 5/5 kỹ thuật.

Ở logs, lời giao general-purpose chứa đầy đủ quy tắc parsing. Báo cáo subagent nói đã kiểm tra schema nhưng tệp dùng timestamp/service_counts; tác tử chính đọc lại, đổi thành timestamp_utc/counts_by_service rồi kiểm tra JSON và tổng đếm. Đây là bằng chứng cần kiểm tra sản phẩm thực, không chỉ tin báo cáo. Vết không chứa các bước bên trong subagent nên không kết luận quá mức về quá trình của nó.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Curator chạy một lần; không xóa hoặc sửa tay skill; không chạy lại. Tổng token curator: 8.889. Prompt, phản hồi nguyên bản và SHA-256 từng skill nằm trong `curator/*.json`; ba tác vụ nguồn đều có role learn, không có tác vụ đánh giá.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| python-bugfix-workflow | Quy trình sửa lỗi package Python; không chứa hàm, đáp án riêng của bài học | Đúng theo feedback: annotations cho hàm public, ít nhất 3 regression test và 3 bullet changelog; áp dụng trong miền Acme | 11 dòng tổng; 7 bước; description bao quát sửa lỗi Python. skills_read được kiểm tra ở Phần 3.4 |
| csv-data-cleaning | Tổng quát theo workflow CSV và schema đầu ra Acme; header clean.csv là quy ước được phép giữ | Giữ integer cents, meta và clean.csv; bước loại amount thiếu phải đọc cùng yêu cầu đếm missing trước khi lọc, không bỏ số đếm cần báo cáo | 15 dòng tổng; 11 bước; description nêu duplicate/inconsistent/money. skills_read được kiểm tra ở Phần 3.4 |
| log-triage-json | Tổng quát cho log có timestamp, multiline và repeat marker | Giữ chuẩn service, sorting và schema; có dòng `=== END===` thừa vì mô hình không viết marker đúng mẫu. Validator vẫn chấp nhận; dòng này không thêm hướng dẫn gây hại | 16 dòng tổng; 11 bước và một marker thừa; description nêu đúng workflow. skills_read được kiểm tra ở Phần 3.4 |

Các quy tắc không phải chuẩn chung cho mọi tổ chức; tính đúng được đánh giá trong miền Acme của lab. Ba skill đều hợp lệ theo validate_skill, ngắn dưới 40 dòng thân, không chứa định danh tập đánh giá và có hash khớp đầu ra curator.

Kết quả Phần 3.4 được sao lưu nguyên vẹn tại `../results/skills-auto-dev/` trước khi chạy lại sau đóng băng:

| Tác vụ | Điểm dev | Skill đã đọc | skills_read | Token | skills_modified |
|---|---|---|---:|---:|---|
| code-learn | 10/10 | python-bugfix-workflow | 1 | 63.856 | false |
| data-learn | 8/8 | csv-data-cleaning | 1 | 17.792 | false |
| logs-learn | 9/9 | log-triage-json | 1 | 39.315 | false |

Vết cho thấy đọc skill phù hợp trước xử lý. Code thêm annotations, regression test và changelog; data ghi integer cents, meta và clean.csv; logs chuẩn hóa tên service, sorting và schema header. Cả 9/9 check quy ước đã đạt trong lần dev, so với 0/9 của baseline. Tác tử code/logs có vài lệnh lỗi do truyền timeout theo mili giây thay vì giây, rồi tự sửa và hoàn thành; đây không phải lỗi API hoặc lần chạy hỏng.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
