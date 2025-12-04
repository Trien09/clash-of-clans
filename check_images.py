import os

print("📁 Checking images folder...")

# Check if images folder exists
if not os.path.exists("images"):
    print("❌ 'images' folder does not exist!")
    print("   Please create 'images' folder and add these files:")
else:
    print("✅ 'images' folder exists")

# List required images
required_images = [
    "attack.png",
    "match.png", 
    "match_begin.png",
    "elixir_cart_empty.png",
    "elixir_cart_third.png", 
    "elixir_cart_half.png", 
    "elixir_cart_full.png",
    "elixir_collect.png"
]

print("\n📋 Required image files:")
print("-" * 40)

missing_count = 0
for img in required_images:
    img_path = os.path.join("images", img)
    if os.path.exists(img_path):
        print(f"✓ {img}")
    else:
        print(f"✗ {img} (MISSING)")
        missing_count += 1

print("-" * 40)
if missing_count == 0:
    print("✅ All images are ready!")
else:
    print(f"❌ Missing {missing_count} image(s)")
    print("\nPlease add the missing images to the 'images' folder.")