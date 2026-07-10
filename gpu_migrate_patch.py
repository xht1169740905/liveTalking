import os
import re

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

PATCHES = [
    {
        'file': 'avatars/wav2lip/face_detection/detection/sfd/sfd_detector.py',
        'changes': [
            (r'^import torch$', 'import torch\ndevice = torch.device(\'cuda\' if torch.cuda.is_available() else \'cpu\')'),
            (r'torch\.load$path_to_detector$', r'torch.load(path_to_detector).to(device)')
        ]
    },
    {
        'file': 'avatars/wav2lip/face_detection/utils.py',
        'changes': [
            (r'^import torch$', 'import torch\ndevice = torch.device(\'cuda\' if torch.cuda.is_available() else \'cpu\')'),
            (r'torch\.from_numpy$tensor$', r'torch.from_numpy(tensor).to(device)')
        ]
    },
    {
        'file': 'avatars/musetalk/utils/face_parsing/__init__.py',
        'changes': [
            (r'^import torch$', 'import torch\ndevice = torch.device(\'cuda\' if torch.cuda.is_available() else \'cpu\')'),
            (r'torch\.load$model_pth$', r'torch.load(model_pth).to(device)')
        ]
    },
    {
        'file': 'avatars/musetalk/utils/face_parsing/resnet.py',
        'changes': [
            (r'^import torch$', 'import torch\ndevice = torch.device(\'cuda\' if torch.cuda.is_available() else \'cpu\')'),
            (r'torch\.load$model_path, weights_only=False$', r'torch.load(model_path, weights_only=False).to(device)')
        ]
    },
    {
        'file': 'avatars/musetalk/utils/face_detection/detection/sfd/sfd_detector.py',
        'changes': [
            (r'^import torch$', 'import torch\ndevice = torch.device(\'cuda\' if torch.cuda.is_available() else \'cpu\')'),
            (r'torch\.load$path_to_detector$', r'torch.load(path_to_detector).to(device)')
        ]
    },
    {
        'file': 'avatars/musetalk/utils/face_detection/utils.py',
        'changes': [
            (r'^import torch$', 'import torch\ndevice = torch.device(\'cuda\' if torch.cuda.is_available() else \'cpu\')'),
            (r'torch\.from_numpy$tensor$', r'torch.from_numpy(tensor).to(device)')
        ]
    },
    {
        'file': 'avatars/ultralight/face_detect_utils/get_landmark.py',
        'changes': [
            (r'^import torch$', 'import torch\ndevice = torch.device(\'cuda\' if torch.cuda.is_available() else \'cpu\')'),
            (r'torch\.load$\'./models/checkpoint_epoch_335\.pth\.tar\'$', r'torch.load(\'./models/checkpoint_epoch_335.pth.tar\').to(device)'),
            (r'torch\.from_numpy$input$$$None$$', r'torch.from_numpy(input)[None].to(device)'),
            (r'PFLDInference$\)\.cuda\($', r'PFLDInference().to(device)'),
            (r'input = input\.cuda\(\)', '')
        ]
    }
]

def apply_patch(filepath, changes):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for pattern, replacement in changes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated: {filepath}")
        return True
    else:
        print(f"✗ No changes: {filepath}")
        return False

def main():
    print("=== GPU Migration Patch Script ===")
    print(f"Project directory: {PROJECT_DIR}")
    print()
    
    changed_count = 0
    for patch in PATCHES:
        filepath = os.path.join(PROJECT_DIR, patch['file'])
        if os.path.exists(filepath):
            if apply_patch(filepath, patch['changes']):
                changed_count += 1
        else:
            print(f"✗ File not found: {filepath}")
    
    print()
    print(f"=== Done! {changed_count}/{len(PATCHES)} files updated ===")

if __name__ == '__main__':
    main()
