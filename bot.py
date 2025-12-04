from time import sleep
import time
from time import sleep
from detection import *

# Tọa độ
ATTACK_BUTTON = (60, 475)
FIRST_TROOP_SLOT = (171, 482)      # Ô quân 1
SECOND_TROOP_SLOT = (300, 324)     # Ô quân 2
GRASS = (730, 85)
TROOP_SLOTS = 6


class Bot:
    def __init__(self, client):
        self.client = client
        print("🤖 Bot initialized!")

    def await_images(self, image_name, confidence=0.9, delay=0.2, max_wait=30):
        """
        Chờ hình ảnh xuất hiện với timeout
        """
        waited = 0
        while waited < max_wait:
            found = locate_image(self.client.capture_screen(), image_name, confidence)
            if found: 
                return found
            sleep(delay)
            waited += delay
        return None

    def is_game_loaded(self):
        """
        Kiểm tra game đã load xong chưa
        """
        # Kiểm tra có nút Attack không
        attack = locate_image(self.client.capture_screen(), ["attack.png"], 0.8)
        return attack is not None

    def wait_for_game_load(self, timeout=60):
        """
        Chờ game load hoàn toàn
        """
        print("🔄 Waiting for game to load...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_game_loaded():
                print("✅ Game loaded successfully!")
                return True
            
            # Thử click vào màn hình để skip loading
            self.client.device.click(400, 300)
            sleep(2)
            
            print(".", end="", flush=True)
        
        print("\n❌ Game loading timeout!")
        return False

    def handle_matching(self):
        """
        Tìm trận - chờ cho đến khi có nút Match
        """
        print("🔍 Finding match...")
        
        # Click nút Attack
        print(f"  → Clicking attack button at {ATTACK_BUTTON}")
        self.client.device.click(*ATTACK_BUTTON)
        sleep(3)  # Chờ màn hình tìm trận load
        
        # Chờ nút Match xuất hiện (có thể mất thời gian)
        print("  → Waiting for match button...")
        match = self.await_images(["match.png"], delay=1, max_wait=30)
        
        if match:
            print(f"  ✅ Found match button at {match}")
            self.client.device.click(*match)
            sleep(2)
            
            # Chờ trận bắt đầu
            print("  → Waiting for battle to start...")
            match_begin = self.await_images(["match_begin.png"], delay=1, max_wait=20)
            if match_begin:
                print("🎮 Battle started!")
                return True
            else:
                print("❌ Battle didn't start properly")
        else:
            print("❌ Match button not found")
        
        return False

    def handle_battle(self):
        """
        Xử lý chiến đấu
        """
        print("👥 Deploying troops...")
        
        # Step 1: Slot 1 - deploy 1 troop
        print(f"  1. Selecting slot 1 at {FIRST_TROOP_SLOT}")
        self.client.device.click(*FIRST_TROOP_SLOT)
        sleep(0.1)
        
        print("     → Deploying 1 troop from slot 1")
        self.client.device.click(*GRASS)
        sleep(0.1)
        
        # Step 2: Slot 2 - deploy 6 troops
        print(f"  2. Selecting slot 2 at {SECOND_TROOP_SLOT}")
        self.client.device.click(*SECOND_TROOP_SLOT)
        sleep(0.1)
        
        print(f"     → Deploying {TROOP_SLOTS} troops from slot 2")
        for i in range(TROOP_SLOTS):
            self.client.device.click(*GRASS)
            sleep(0.1)
        
        sleep(1)  # CANNOT BE LOWER
        print(f"✅ Deployed: 1 troop from slot 1 + {TROOP_SLOTS} troops from slot 2")

    def handle_restart(self):
        """
        Khởi động lại game và chờ load hoàn toàn
        """
        print("🔄 Restarting game...")
        
        try:
            # Dừng game
            self.client.device.app_stop('com.supercell.clashofclans')
            sleep(2)
            
            # Khởi động lại
            self.client.device.app_start(
                package_name='com.supercell.clashofclans', 
                activity='com.supercell.titan.GameApp'
            )
            sleep(5)  # Chờ game khởi động
            
            # Chờ game load hoàn toàn
            if not self.wait_for_game_load():
                print("❌ Game didn't load properly, trying force restart...")
                return False
            
            print("✅ Game restarted and loaded!")
            return True
            
        except Exception as e:
            print(f"❌ Error restarting game: {e}")
            return False

    def handle_elixir(self):
        """
        Thu thập elixir
        """
        print("💰 Checking elixir cart...")
        
        attempts = 0
        while attempts < 20:  # Thử trong 20 lần
            cart_images = [
                "elixir_cart_empty.png", "elixir_cart_third.png", 
                "elixir_cart_half.png", "elixir_cart_full.png"
            ]
            
            cart = locate_image(self.client.capture_screen(), cart_images, 0.6)
            if cart:
                print(f"✅ Found cart at {cart}")
                self.client.device.click(*cart)
                sleep(1)
                
                collect = locate_image(self.client.capture_screen(), ["elixir_collect.png"], 0.9)
                if collect:
                    print(f"✅ Found collect button at {collect}")
                    self.client.device.click(*collect)
                    sleep(1)
                    self.client.device.shell("input keyevent KEYCODE_BACK")
                    print("💰 Elixir collected!")
                    return True
                else:
                    print("❌ Collect button not found, going back...")
                    self.client.device.shell("input keyevent KEYCODE_BACK")
                    sleep(1)
            
            sleep(1)
            attempts += 1
        
        print("⚠️ No elixir cart found, continuing...")
        return False

    def run(self):
        """
        Vòng lặp chính
        """
        print("=" * 50)
        print("🚀 STARTING BOT")
        print("=" * 50)
        
        import time
        cycle = 0
        
        while True:
            cycle += 1
            print(f"\n{'='*30}")
            print(f"♻️ CYCLE #{cycle}")
            print(f"{'='*30}")
            
            try:
                # 1. Thu thập elixir
                print("\n[1/4] Collecting elixir...")
                elixir_collected = self.handle_elixir()
                
                if not elixir_collected:
                    print("⚠️ Skipping elixir collection...")
                
                # 2. Tìm trận (thử nhiều lần nếu cần)
                print("\n[2/4] Finding match...")
                match_found = False
                for attempt in range(3):  # Thử 3 lần
                    print(f"  Attempt {attempt + 1}/3...")
                    if self.handle_matching():
                        match_found = True
                        break
                    else:
                        print("  Retrying in 5 seconds...")
                        sleep(5)
                
                if not match_found:
                    print("❌ Could not find match after 3 attempts")
                    print("🔄 Restarting game and trying again...")
                    self.handle_restart()
                    continue
                
                # 3. Thả quân
                print("\n[3/4] Deploying troops...")
                self.handle_battle()
                
                # Chờ kết thúc trận (ước lượng)
                print("⏳ Waiting for battle to end (approx 30s)...")
                sleep(30)
                
                # 4. Khởi động lại game
                print("\n[4/4] Restarting game...")
                restart_success = self.handle_restart()
                
                if restart_success:
                    print(f"✅ Completed cycle #{cycle}")
                else:
                    print("❌ Restart failed, trying again...")
                
                # Nghỉ ngắn giữa các chu kỳ
                print("\n⏳ Waiting 5 seconds before next cycle...")
                sleep(5)
                
            except KeyboardInterrupt:
                print("\n\n⏹ Bot stopped by user!")
                break
            except Exception as e:
                print(f"\n⚠️ Unexpected error: {e}")
                print("Retrying in 10 seconds...")
                sleep(10)