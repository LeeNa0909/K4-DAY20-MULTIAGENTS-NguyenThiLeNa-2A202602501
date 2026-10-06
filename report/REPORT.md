# Báo cáo Lab: Self evolving Agentic

Ngày thực hiện: 06/10/2026 (Asia/Saigon). Bản ghi thời gian của runner dùng UTC.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| NguyenThiLeNa (theo tên kho) | 2A202602501 | Thực hiện lab với hỗ trợ AI: harness, thí nghiệm, phân tích và báo cáo |

- Mô hình: `openai/gpt-6-luna` qua OpenRouter (`https://openrouter.ai/api/v1`), `LAB_TEMPERATURE=0`, `recursion_limit=60`.
- Deep Agents: `0.7.21`; Ubuntu WSL trên Windows; Python Linux `3.14.4`. Môi trường chạy chính: `/root/.local/share/lab-k4-day20-venv`; không dùng Docker. Phiên bản phụ thuộc được lưu trong `requirements-freeze.txt`.
- Tổng: 22 lần chạy tác vụ (18 chính thức, 3 dev trước đóng băng, 1 bản đầu có vấn đề CRLF); curator 1 lần và kiểm tra kết nối 1 lần. Tổng token đo được của tác vụ và curator: 1.203.048, chưa tính lời gọi kiểm tra kết nối; test ngoại tuyến không gọi API. Tài liệu hiện tại không nêu ngân sách số lần chạy cụ thể.
- Commit của tag `freeze`: `ea8be84e81bd1caec830d384a5927fbab62eadee`, 06/10/2026 12:14:17 +07:00; commit hypotheses `17813bc` lúc 12:13:52 +07:00 đứng trước tag.

Cấu hình được make_model đọc (khóa riêng trong .env, không đưa vào git):

```dotenv
AZURE_OPENAI_ENDPOINT=https://openrouter.ai/api/v1
AZURE_OPENAI_KEY=<OpenRouter API key>
AZURE_OPENAI_DEPLOYMENT_MODEL=openai/gpt-6-luna
LAB_TEMPERATURE=0
```

Project này không đọc LLM_PROVIDER hoặc EMBEDDING_PROVIDER và không có pipeline embedding.

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

Trên tập đánh giá: code-eval gọi explorer 1 lần, data-eval gọi general-purpose 1 lần, logs-eval gọi explorer và reviewer (2 lần). Ở code-eval, tác tử chính yêu cầu explorer sửa code nhưng explorer giữ đúng system prompt chỉ đọc, nên tác tử chính tự thực hiện. Reviewer ở logs-eval được gọi trước khi có tệp đầu ra và báo rõ giới hạn đó. Tổng cộng cả sáu tác vụ có 8 lần gọi task; không phải mọi lời giao việc đều chọn đúng vai trò hoặc truyền đủ ngữ cảnh.

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

Nội dung nguyên bản do `python -m lab.compare` sinh trong `table.md`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 10/10 |
| data-learn | 5/8 | 5/8 | 7/8 |
| logs-learn | 6/9 | 6/9 | 9/9 |
| code-eval | 7/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 6/9 |
| logs-eval | 6/10 | 6/10 | 9/10 |
| **Mean score - learning tasks** | 0.66 | 0.66 | 0.96 |
| **Mean score - evaluation tasks** | 0.60 | 0.60 | 0.83 |
| **Mean tokens per run** | 34,115 | 78,397 | 53,273 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Thống kê nguyên bản từ `scripts/check_breakdown.py`, lưu trong `check_breakdown.txt`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12          30,069      0/3
baseline      learn    18/18         0/9           38,161      0/3
subagents     eval     18/18         0/12          77,345      0/3
subagents     learn    18/18         0/9           79,449      0/3
skills-auto   eval     18/18         7/12          48,619      3/3
skills-auto   learn    18/18         8/9           57,927      3/3
```

Mỗi điểm trung bình là trung bình tỉ lệ đạt của từng tác vụ, không phải gộp số check. Bảng hiển thị điểm với hai chữ số thập phân và phần nguyên của token trung bình; `metrics.json` giữ số liệu đầy đủ để tính chênh lệch. Cả 18 bản ghi chính thức có error=null, skills_modified=false và tokens.total>0. Sáu bản ghi skills-auto đều dùng hash `43a6a2a8e1a2c48bf064218783eaf05859f546e945c3e635227837a97dcd11cc`.

`verify_freeze.txt`: `checked 6 runs of skill conditions: OK`. Lần kiểm tra đầu báo diff ở README gốc của skills/ vì Git Windows và WSL có cách xử lý CRLF khác nhau; đối chiếu byte xác nhận cả ba SKILL.md vẫn đúng hash curator. Đặt core.autocrlf=true riêng cho repo để thống nhất Git; không thay đổi bytes của skill. Kết quả kiểm tra sau đó đạt, không cần chạy lại thí nghiệm.

## 8. Phân tích

1. **So sánh và giả thuyết.** Skills-auto cải thiện điểm học từ 0,6639 lên 0,9583 (+29,44 điểm phần trăm), và điểm đánh giá từ 0,5973 lên 0,8253 (+22,79 điểm phần trăm). Subagents có điểm bằng baseline ở mọi tác vụ. H1 và H2 phù hợp số liệu của lần chạy này; chưa phải kiểm định thống kê. H3 cũng phù hợp về hướng: mức cải thiện trên đánh giá thấp hơn trên học 6,65 điểm phần trăm. Skills-auto cải thiện cả hai tập, nhưng chuyển giao không đầy đủ, đặc biệt ở data-eval chỉ tăng từ 5/9 lên 6/9.

2. **Kỹ thuật và quy ước.** Cả ba điều kiện đều đạt 18/18 kỹ thuật trên mỗi tập; có hiệu ứng trần nên không chứng minh skill cải thiện kỹ thuật. Skills-auto tăng check quy ước từ 0/9 lên 8/9 trên học và 0/12 lên 7/12 trên đánh giá. Ba quy ước mới đều thất bại: rule_version_bump ở code-eval, rule_sorted_keys_format ở data-eval, rule_source_line ở logs-eval. Bộ skill đóng băng không có quy trình tăng patch version, JSON sort_keys/indent/newline hoặc lưu số dòng nguồn. Các định nghĩa checker này chỉ được xem sau đóng băng, không được đưa lại vào skill.

3. **Cơ chế và trường hợp không chuyển giao.** Ở code-eval, read_file đọc python-bugfix-workflow, sau đó tác tử thêm annotations, tests/test_regressions.py và CHANGELOG.md; ba check tương ứng chuyển từ thất bại sang đạt. Skill đã đọc nhưng thiếu version bump nên check mới vẫn không đạt. Logs-eval đọc skill log và thích nghi với ERROR/SEVERE/FATAL của đề mới, đồng thời giữ chuẩn service, sorting và schema: 9/10; thiếu source_line. Data-eval đọc csv-data-cleaning nhưng viết CSV header có region, còn category được điền chuỗi rỗng trong clean_rows, thay vì header category và giá trị category chuẩn hóa. Trace còn tự assert header cũ và báo Validation passed: đây là kiểm chứng lặp lại giả định sai. meta.source là workspace/orders.json thay vì tên tệp đơn thuần, nên metadata thất bại dù rows_in/rows_used đúng. Quy tắc integer cents vẫn giúp đạt. Những lỗi này cho thấy đọc skill không đồng nghĩa áp dụng đúng hoặc thích nghi schema; skill CSV thiếu linh hoạt khi đổi định dạng và loại trường.

4. **Chi phí.** Trung bình cả sáu tác vụ: baseline 34.115 token, subagents 78.397 (2,30× baseline), skills-auto 53.273 (1,56×). Thời gian trung bình tương ứng 38,9 / 89,2 / 50,4 giây; thời gian runner đo trước bước chấm điểm. Điểm trung bình toàn bộ tương ứng 0,6306 / 0,6306 / 0,8918. Chỉ số điểm trung bình trên 1.000 token = tổng score / tổng token × 1.000 là 0,018484 / 0,008044 / 0,016740: baseline hiệu quả nhất theo chỉ số này, skills-auto đạt điểm cao nhất. Subagents chưa mang lại lợi ích điểm để bù token trong thí nghiệm; chưa suy rộng sang tác vụ lớn hoặc cần song song. Token là đại diện chi phí, không phải hóa đơn USD; chưa xét giá cache hay chi phí khác.

5. **Rò rỉ và quá khớp.** Curator chỉ nhận ba baseline học; validator chặn định danh đánh giá và tên đường dẫn không an toàn; audit lưu nguyên prompt/reply/hash. H1–H3 đã commit trước tag; mọi lần chính thức dùng cùng hash skill và không sửa skill. Không thấy bằng chứng rò rỉ tập đánh giá vào skill. Header region cố định và việc áp dụng nó cho JSON category là bằng chứng cụ thể của quy trình phụ thuộc biểu diễn bài học. Đây là dấu hiệu chuyển giao kém; khoảng cách điểm tổng hợp còn bị ảnh hưởng bởi quy ước mới và độ khó, nên không quy toàn bộ chênh lệch cho quá khớp.

6. **Dao động khi chạy lại cùng skill.** Bản dev được giữ nguyên và có cùng skills_sha256 với bản sau đóng băng:

| Tác vụ học | Điểm dev | Điểm chính thức | Chênh lệch score | Token dev / chính thức |
|---|---|---|---:|---:|
| code-learn | 10/10 | 10/10 | 0 | 63.856 / 84.551 |
| data-learn | 8/8 | 7/8 | -0,125 | 17.792 / 38.054 |
| logs-learn | 9/9 | 9/9 | 0 | 39.315 / 51.178 |

Điểm học trung bình giảm từ 1,0000 xuống 0,9583, chênh 4,17 điểm phần trăm. data-learn sau đóng băng ghi meta.source=workspace/sales.csv, trong khi dev dùng basename và đạt check. Đây là dao động trong việc thực hiện quy tắc của cùng bộ skill; temperature=0 không bảo đảm mọi lần giống nhau. Token cũng thay đổi đáng kể. Hai lần trên ba tác vụ chỉ cung cấp một quan sát độ dao động, không đủ ước lượng phương sai hoặc khoảng tin cậy; các chênh lệch nhỏ cần nhiều lần lặp hơn.

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba tác vụ mỗi tập và một lần chính thức mỗi điều kiện; các kết quả không đại diện mọi workload và không đủ kiểm định khác biệt nhỏ.
2. Chỉ một model alias qua OpenRouter, không chốt seed hay phiên bản máy phục vụ; hai lần cùng skill đã có chênh lệch 4,17 điểm phần trăm trên điểm học trung bình. Không coi temperature=0 là bảo đảm tái lập từng byte.
3. Tác vụ được thiết kế có quy ước ẩn và feedback học; lợi ích chủ yếu là lưu tri thức Acme. Check kỹ thuật đều đạt trần, nên không suy ra cải thiện năng lực sửa code/parsing tổng quát.
4. Tập đánh giá đổi biểu diễn và thêm quy ước chưa được phản hồi; khoảng cách học/đánh giá trộn nhiều nguyên nhân, chưa tách riêng tác động quá khớp, invocation và schema shift.
5. Trace chỉ có luồng chính và cắt mỗi đoạn/args ở 1.500 ký tự; không quan sát đầy đủ nội bộ subagent hoặc mọi sản phẩm trung gian. Count công cụ/subagent/skill chỉ tính luồng chính, trong khi token tính cả subagent.
6. Thư mục sandbox chỉ chứa bản sao workspace và env shell được giới hạn; đây không phải cô lập hệ điều hành bằng container. Giữ nguyên task gốc được kiểm tra bằng test và audit Git; các khó khăn CRLF/Git được ghi riêng như vấn đề hạ tầng.

## 10. Kết luận

Trong sáu tác vụ này, skills-auto đạt điểm cao nhất nhờ giữ lại phần lớn quy ước Acme đã học, với điểm đánh giá trung bình 0,8253 so với baseline 0,5973. Subagents không tăng điểm và dùng 2,30 lần token của baseline. Skill CSV được đọc nhưng áp dụng sai metadata và schema ở một số lần, nên skill hợp lệ về định dạng chưa bảo đảm chuyển giao. Lần chạy lại cùng skill làm điểm học trung bình giảm 4,17 điểm phần trăm, cho thấy cần đánh giá lặp. Nghiên cứu tiếp theo nên làm rõ basename và schema theo data dictionary trong phản hồi tập học, sinh lại skill bằng curator rồi đánh giá trên tập giữ riêng mới với nhiều lần lặp.

## Phụ lục

Theo README mục 5, bộ nộp trong `report/` chỉ gồm `REPORT.md` và `table.md`. Các log, snapshot phụ thuộc, thống kê trung gian, `CHECKPOINTS.md` và công cụ `verify_artifacts.py` được nhắc trong báo cáo là tài liệu kiểm tra cục bộ, đã đưa vào `.gitignore`. Bằng chứng nộp nằm trong báo cáo này, bảng so sánh và các `run.json`/`trace.md` thuộc `results/`.

Các lệnh cốt lõi dưới đây được viết gọn tương đương các lời gọi `wsl -d Ubuntu --exec ...` đã chạy trong thư mục gốc. Các bước triển khai source và test ngoại tuyến có thể đối chiếu với CHECKPOINTS.md; các lần gọi API thực hiện tuần tự theo thứ tự thí nghiệm.

```bash
LAB_PYTHON=/root/.local/share/lab-k4-day20-venv/bin/python
$LAB_PYTHON -m pytest tests/test_01_provided.py
$LAB_PYTHON -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"
$LAB_PYTHON scripts/tour.py
$LAB_PYTHON -m pytest tests/test_02_agent.py
$LAB_PYTHON -m pytest tests/test_03_runner.py
$LAB_PYTHON -m lab.runner --condition baseline --tasks data-learn
$LAB_PYTHON -m lab.runner --condition baseline --tasks code-learn logs-learn
# Sao lưu bản code-learn có vấn đề CRLF rồi chạy lại sau khi sửa runner.
$LAB_PYTHON -m lab.runner --condition baseline --tasks code-learn
$LAB_PYTHON -m lab.runner --condition subagents --tasks learn
$LAB_PYTHON -m pytest tests/test_04_curator.py
$LAB_PYTHON -m pytest
$LAB_PYTHON -m lab.curator
$LAB_PYTHON -m lab.runner --condition skills-auto --tasks learn
# Đã sao lưu results/skills-auto sang results/skills-auto-dev bằng Copy-Item.
git add src/lab/agent.py src/lab/subagents.py src/lab/runner.py src/lab/curator.py report results skills/auto
git commit -m hypotheses
git commit --allow-empty -m "freeze skills"
git tag freeze
$LAB_PYTHON -m lab.runner --condition baseline --tasks eval
$LAB_PYTHON -m lab.runner --condition subagents --tasks eval
$LAB_PYTHON -m lab.runner --condition skills-auto --tasks all
git config --local core.autocrlf true
$LAB_PYTHON scripts/verify_freeze.py
$LAB_PYTHON -m lab.compare > report/table.md
$LAB_PYTHON scripts/check_breakdown.py > report/check_breakdown.txt
$LAB_PYTHON report/verify_artifacts.py
```

Để kiểm tra bộ nộp sau khi clone, cài project theo README trong môi trường Linux, chạy `python -m pytest`, `python scripts/verify_freeze.py` và `python -m lab.compare`. Tại workspace gốc còn có công cụ kiểm tra bổ sung `report/verify_artifacts.py` và snapshot môi trường `requirements-freeze.txt` chỉ lưu cục bộ. Khi clone trên Windows để đối chiếu hash, giữ LF cho SKILL.md; các file này được curator tạo bằng LF và hash dựa trên bytes. Tái chạy thí nghiệm dùng --results thư mục khác để giữ các kết quả hiện tại.

29 test ngoại tuyến đạt (pytest.txt). Audit kiểm tra 18 bản ghi, bảng compare, ba bản dev, nguyên bản skill từ curator, các tệp/hàm được cung cấp và khóa API trong artifact (artifact_audit.txt). Phần 6 của GUIDE là thử thách tùy chọn; bộ kết quả này thực hiện các checkpoint bắt buộc 0–5. GUIDE có tham chiếu README mục 2.3 và 7 không tồn tại trong bản README hiện tại; quy trình áp dụng các chỉ dẫn cụ thể trong GUIDE và RUBRIC.

Tài liệu tham khảo chính: [SkillsBench](https://arxiv.org/abs/2602.12670), [SkillEvolBench](https://skillevolbench.github.io/), [Anthropic multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system). Các dự đoán ở mục 2 là suy luận cho lab từ tài liệu và dữ liệu học, không phải kết luận có sẵn của các nguồn này.
