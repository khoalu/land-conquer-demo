# LAND CONQUER - Trình chấm
_Note_: Hãy đọc đề trước khi đọc file này
_Note 2_: Toàn bộ các lệnh dưới đây đều được test trên Windows 10. Nếu thí sinh nào dùng Linux và không chạy được các lệnh dưới hãy liên hệ BTC để được giải đáp. 
## Requirement
1. [python3](https://www.python.org/)
* Tải [ở đây](https://www.python.org/downloads/) (nhớ cài cả pip đi kèm với python)  

2. [pygame](https://www.pygame.org/news)

* Cài đặt ```pygame```:
	```
	pip install pygame
	```
## File structure

### Simple file structure
```
land-conquer/
 data/
  player0/
   game.exe
  player1/
   game.exe
 log/
 maps/
 config.json
 main.py
```
Trên đây là những file/folder các thí sinh cần nắm

### Complete file structure
```
land-conquer/
 data/
  player0/
   game.exe
   make.bat
  player1/
   game.exe
   make.bat
 log/
 maps/
 sprites/
 
 config.json
 
 main.py
 gamestate.py
 manager.py
 
 autoclean.bat
 autocompile.bat
 readme.md (file này)
```

## Cách chạy trình chấm đơn giản 
1. Xóa toàn bộ file trong folder ```log/```
2. Copy 2 file ```game.exe``` được dịch từ code thí sinh vào 2 thư mục lần lượt là ```data/player0/game.exe``` và ```data/player1/game.exe``` 
3. Chỉnh file ```config.json```
	* ```players_names```: tên của 2 người chơi (không dấu)
	* ``` time_limit_per_turn```: số giây tối đa để thực thi 1 lượt
	* ``` max_turn```: số lượt tối đa
	* ```initial_moves```: số hành động tối đa trong 1 lượt
	* ```initial_drills```: số khoan để phá tường
	* ```layout```: tên của map trong folder ```maps```. BTC sẽ cung cấp sẵn vài map để các thí sinh chơi thử
	
	--- không quan trọng lắm ---
	* ``` draw_cell_point ```: có vẽ điểm số của ô hay không ?
	* ``` time_per_display_phase ```: mỗi pha update + display chạy bao lâu ? (tính bằng giây)
4. Chạy ```python main.py ```

## Flow của trình chấm (file ```main.py```)
1. Đọc file ```config.json``` 
2. Chạy 2 file ```.exe``` của 2 thí sinh thi đấu với nhau, sau đó ghi toàn bộ lịch sử vào folder ```log/``` với 3 files mỗi lượt ```<turn>_input.log``` ,```<turn>_output0.log```, ```<turn>_output1.log ``` 
    * method ```Game.run_player_program()``` trong ```main.py```
3. Đọc folder ```log/``` và hiển thị lên màn hình bằng module ```pygame``` 
    * method ```Game.run()``` trong ```main.py```
    * Mỗi lượt sẽ gồm 5 giai đoạn:
	    1. Đọc hành động của 2 người chơi từ folder ```log/```
	    2. Thể hiện hành động của người chơi 
	    3. Thực hiện các hành động lên bản đổ và cập nhật bản đồ
	    4. Cập nhật các zones (khu vực ma thuật)
	    5. Loại bỏ các zones đã được kích hoạt

Thí sinh có thể chạy bước 2 và bước 3 riêng rẽ bằng cách:
* Chỉ chạy bước 2: ```python main.py 0```
* Chỉ chạy bước 3: ```python main.py 1```

## Tạo 1 map mới
Các map được tạo nằm trong folder ```maps/```, có dạng
```
n
<color_board>
<blank line>
<env_board>
<blank line>
<point_board>
<blank line>
nZone
<zones>
```
Trong đó:
* ```color_board```: ```n``` dòng, mỗi dòng ```n``` số cách nhau bởi khoảng trắng, cho biết ai đang chiếm ô này
* ```env_board```: ```n``` dòng, mỗi dòng ```n``` số cách nhau bởi khoảng trắng, cho biết ô này đang có gì (trống hay chứa vật phẩm/môi trường nào đó)
* ```point_board```: ```n``` dòng, mỗi dòng ```n``` số cách nhau bởi khoảng trắng, cho biết ô này có bao nhiêu điểm
* ```zones``` ```nZone``` dòng, mỗi dòng 5 số, thể hiện zone
* ```blank line```: dòng trống

Tất cả các số đều theo mô tả trong file đề (các thí sinh lúc test có thể tăng các giới hạn tùy ý)