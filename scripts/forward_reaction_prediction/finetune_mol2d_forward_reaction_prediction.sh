#!/bin/bash

# set as environment variables
export MOLECULE_2D_PATH="/gpfs/gibbs/pi/gerstein/xt86/bioagent/checkpoints/MoleculeSTM/"
export WANDB_API_KEY="8d2eaed6c14b0b07e12ac075af68b8ee1c372483"

MODEL_VERSION=lmsys/vicuna-7b-v1.5
MODEL_CLS=LlamaLMMForCausalLM
DATA_DIR="/gpfs/gibbs/pi/gerstein/xt86/bioagent/data/Mol-Instructions/data/Molecule-oriented_Instructions/forward_reaction_prediction/train"
OUTPUT_DIR="/gpfs/gibbs/pi/gerstein/xt86/bioagent/checkpoints/llava-moleculestm-$MODEL_VERSION-forward-reaction-prediction"
PROJECTOR_DIR="/gpfs/gibbs/pi/gerstein/xt86/bioagent/checkpoints/llava-moleculestm-$MODEL_VERSION-pretrain/non_lora_trainables.bin"

deepspeed ../train_model.py \
    --model_name_or_path $MODEL_VERSION \
    --model_cls $MODEL_CLS \
    --modality_builder molecule_2d \
    --dataset_path $DATA_DIR \
    --output_dir $OUTPUT_DIR \
    --pretrained_projectors_path $PROJECTOR_DIR \
    --lora_enable True \
    --bf16 True \
    --tf32 True \
    --num_train_epochs 10 \
    --gradient_checkpointing True \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 4 \
    --gradient_accumulation_steps 2 \
    --model_max_length 4096 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 500 \
    --save_total_limit 1 \
    --learning_rate 8e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --dataloader_num_workers 2 \
    --logging_steps 1 \
    --report_to wandb \
    --deepspeed ../../configs/zero2.json