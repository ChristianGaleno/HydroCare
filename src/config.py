class CFG:
    # --- data ---
    # Point this at the folder that DIRECTLY contains the class subfolders.
    # Tip: run the auto-detect cell below if you're unsure of the exact path.
    IMAGE_SIZE   = 224
    BATCH_SIZE   = 512
    NUM_WORKERS  = 2
    VAL_SPLIT    = 0.15
    TEST_SPLIT   = 0.15
    # ImageNet normalization (required for pretrained weights)
    MEAN = [0.485, 0.456, 0.406]
    STD  = [0.229, 0.224, 0.225]

    # --- training ---
    EPOCHS         = 20
    FREEZE_EPOCHS  = 4        # train only the head for these many epochs first
    UNFREEZE_STAGES = 2       # how many trailing ResNet stages to unfreeze after
    LR_HEAD        = 1e-3
    LR_FINETUNE    = 1e-4
    WEIGHT_DECAY   = 1e-4
    LABEL_SMOOTH   = 0.1
    PATIENCE       = 6        # early-stopping patience (epochs)
    SEED           = 42

    # --- output ---
    OUT_DIR        = "/kaggle/working"
    CKPT_NAME      = "best_resnet50.pt"

cfg = CFG()