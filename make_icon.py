from PIL import Image
import os

def create_ico(source_png, target_ico):
    if not os.path.exists(source_png):
        print(f"Ошибка: Файл {source_png} не найден!")
        return

    img = Image.open(source_png)
    
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    img.save(target_ico, sizes=icon_sizes)
    print(f"Успешно создана иконка: {target_ico}")

if __name__ == "__main__":
    create_ico("frontend/public/logo.png", "frontend/public/app_icon.ico")