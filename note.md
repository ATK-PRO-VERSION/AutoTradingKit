Thêm 1 số indicators PANDAS-TA

**Celery**: thư viện chạy tác vụ nền

https://pypi.org/project/celery/


https://github.com/twopirllc/pandas-ta/pull/661/files#diff-45fcc49d657dcb2c763943b43322a3c91d2b054484f0d1e2d18388ae3124e714

build Ta_lib
https://github.com/cgohlke/talib-build/
d:/AutoTradingKit/venv/Scripts/python.exe -3.12 -m pip install TA_Lib-0.4.32-cp312-cp312-win_amd64.whl

Khi sử dụng lệnh `cythonize`, bạn có thể cung cấp nhiều tham số để tinh chỉnh quá trình biên dịch. Dưới đây là một số tham số phổ biến mà bạn có thể sử dụng:

1. **-3, --3** : Kiểm tra cú pháp và sử dụng Python 3 trong quá trình biên dịch.
2. **-a, --annotate** : Tạo các tệp HTML chứa thông tin về cách mã Python được biên dịch thành mã C.
3. **-f, --force** : Buộc Cython biên dịch tất cả các tệp, kể cả những tệp đã được biên dịch từ trước.
4. **-j, --jobs** : Số lượng công việc song song được chạy trong quá trình biên dịch.
5. **-p, --prune** : Xóa các tệp `.c` sau khi đã biên dịch chúng thành các module mở rộng.
6. **-X, --compiler-options** : Chỉ định các tùy chọn cụ thể cho trình biên dịch C. Ví dụ: `-X language_level=3` để chỉ định Python 3.
7. **--build-dir** : Đặt thư mục nơi các tệp tạm được tạo trong quá trình biên dịch.
8. **-i, --inplace** : Đặt các tệp kết quả trong cùng thư mục với các tệp nguồn.
9. **-j, --nthreads** : Số lượng luồng được sử dụng cho việc biên dịch song song.
10. **--force** : Buộc Cython biên dịch lại tất cả các tệp, kể cả những tệp đã được biên dịch từ trước.
11. **--build-dir** : Đặt thư mục nơi các tệp tạm được tạo trong quá trình biên dịch.
12. **--cleanup** : Xóa các tệp tạm thời được tạo trong quá trình biên dịch sau khi kết thúc.
13. **--compiler-options** : Chỉ định các tùy chọn cụ thể cho trình biên dịch C.
14. **--line-directives** : Bao gồm thông tin về nguồn gốc dòng cho các lệnh mã biên dịch.
15. **--work** : Sử dụng chế độ làm việc nhanh hơn, nhưng sử dụng nhiều bộ nhớ hơn.
16. **--lenient** : Cho phép Cython tiếp tục biên dịch nếu có lỗi.
17. **--gdb** : Tạo mã có thể được gỡ lỗi bằng GDB.
18. **--pdb** : Tạo mã có thể được gỡ lỗi bằng PDB.
19. **--no-docstrings** : Loại bỏ chuỗi tài liệu từ mã đầu ra.

Dưới đây là một ví dụ về việc sử dụng `cythonize` với một số tham số:

"cythonize --inplace -3 --force -j 4 --p --compiler-options=-O3 --cleanup example.pyx"

Lệnh này sẽ biên dịch `example.pyx` thành một extension
Python, sử dụng Python 3 và tạo các tệp HTML chứa thông tin về cách mã
Python được biên dịch. Nó cũng buộc Cython biên dịch lại tất cả các tệp,
 sử dụng 4 công việc song song và sau đó xóa các tệp `.c` tạm thời. Cuối cùng, nó sử dụng tùy chọn trình biên dịch `-O3` để tối ưu hóa mã C.

Tùy chọn `--compiler-options=-O3` trong lệnh `cythonize` cho biết Cython sẽ chuyển các tùy chọn `'-O3'` cho trình biên dịch C khi biên dịch mã Python thành mã C.

Trong trường hợp này, `-O3` là một tùy chọn tối ưu hóa của trình biên dịch C. Trong nhiều trình biên dịch C như GCC (GNU Compiler Collection), `-O3` là một tùy chọn tối ưu hóa mạnh mẽ, cho phép trình biên dịch thực hiện nhiều loại tối ưu hóa mã cảm biến, loại bỏ mã chết, và tối ưu hóa vòng lặp, giữa các tùy chọn khác.

Khi bạn cung cấp tùy chọn `-O3` cho trình biên dịch C thông qua Cython, mã C được sinh ra sẽ được biên dịch với các tối ưu hóa mạnh mẽ hơn, điều này có thể cải thiện hiệu suất của mã khi chạy. Tuy nhiên, hãy lưu ý rằng việc sử dụng các tùy chọn tối ưu hóa cao có thể làm tăng thời gian biên dịch và kích thước của các tệp mã.

Có nhiều tùy chọn tối ưu hóa khác nhau có thể được sử dụng với trình biên dịch C, bao gồm các cấp độ tối ưu hóa và các tùy chọn cụ thể cho từng loại tối ưu hóa. Dưới đây là một số tùy chọn tối ưu hóa phổ biến:

1. **-O0** : Không tối ưu hóa. Sử dụng cấp độ tối ưu hóa thấp nhất.
2. **-O1** : Tối ưu hóa cơ bản. Áp dụng các tối ưu hóa nhẹ nhàng như loại bỏ mã chết.
3. **-O2** : Tối ưu hóa trung bình. Áp dụng các tối ưu hóa về cơ bản cùng với một số tối ưu hóa về hiệu suất.
4. **-O3** : Tối ưu hóa đầy đủ. Áp dụng tất cả các loại tối ưu hóa có sẵn, bao gồm cả tối ưu hóa mã cảm biến và tối ưu hóa vòng lặp.
5. **-Ofast** : Tối ưu hóa nhanh. Áp dụng các tối ưu hóa về hiệu suất mà không đảm bảo tính ổn định của mã.
6. **-Os** : Tối ưu hóa kích thước. Tối ưu hóa để giảm kích thước của các tệp thực thi.
7. **-Og** : Tối ưu hóa đội ngũ. Tối ưu hóa cho việc gỡ lỗi và tối ưu hóa cho tốc độ biên dịch.

   *Khi nào update CCXT thì sửa hàm này trong

   venv\Lib\site-packages\ccxt\async_support\base\exchange.py

   ```
   def watch(self, url, message_hash, message=None, subscribe_hash=None, subscription=None):
           # base exchange self.open starts the aiohttp Session in an async context
           self.open()
           backoff_delay = 0
           client = self.client(url)
           if subscribe_hash is None and message_hash in client.futures:
               return client.futures[message_hash]
           future = client.future(message_hash)

           subscribed = client.subscriptions.get(subscribe_hash)

           if not subscribed:
               client.subscriptions[subscribe_hash] = subscription or True

           connected = client.connected if client.connected.done() \
               else asyncio.ensure_future(client.connect(self.session, backoff_delay))

           def after(fut):
               # todo: decouple signing from subscriptions
               options = self.safe_value(self.options, 'ws')
               cost = self.safe_value(options, 'cost', 1)
               if message:
                   async def send_message():
                       if self.enableRateLimit:
                           await client.throttle(cost)
                       try:
                           await client.send(message)
                       except ConnectionError as e:
                           client.on_error(e)
                       except Exception as e:
                           client.on_error(e)
                   asyncio.ensure_future(send_message())
   	"đây là đoạn sửa, để check internet conection"
           # if not subscribed:
           #     connected.add_done_callback(after)
           connected.add_done_callback(after)

           return future
   ```
