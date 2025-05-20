from ultralytics import YOLO
import yaml
import torch

def main():
    print("CUDA available:", torch.cuda.is_available())
    print("CUDA device name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU found")

    DATASET_PATH = "F:\\Documents\\GitHub\\T-Rex Game RL\\datasets"

    data_yaml = {
        'train': f'{DATASET_PATH}/train/images',
        'val': f'{DATASET_PATH}/valid/images',
        'nc': 10,
        'names' : [
            "Cactus-1pcs",
            "Cactus-2pcs",
            "Cactus-S-1pcs",
            "Cactus-S-2pcs",
            "Cactus-S-3pcs",
            "Cactus-big",
            "Living-Dino",
            "Dino-player-dead",
            "Dino-player-crouch",
            "Flying-Dino",
        ],
    }

    yaml_path = f'{DATASET_PATH}/train_data.yaml'
    with open(yaml_path, 'w') as file:
        yaml.dump(data_yaml, file, default_flow_style=False)

    model = YOLO('yolov8n.pt')
    results = model.train(data=yaml_path, epochs=100, imgsz=640, device='cuda')

    metrics = model.val(data=yaml_path)
    print(metrics)

if __name__ == '__main__':
    torch.multiprocessing.freeze_support()  # This ensures compatibility if you compile the script
    main()