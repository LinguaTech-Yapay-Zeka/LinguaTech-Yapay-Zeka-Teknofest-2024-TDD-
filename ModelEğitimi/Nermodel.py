from transformers import  TrainingArguments, Trainer
from datasets import load_dataset
import torch
from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer
from transformers import DataCollatorForTokenClassification
import evaluate
import numpy as np
from transformers import pipeline


dataset = load_dataset("turkish-nlp-suite/turkish-wikiNER")

model_name = "dbmdz/bert-base-turkish-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

label2id = {
    'O': 0,
    'B-PER': 1,
    'I-PER': 2,
    'B-ORG': 3,
    'I-ORG': 4,
    'B-LOC': 5,
    'I-LOC': 6,
}

id2label = {i: label for label, i in label2id.items()}

def align_labels_with_tokens(labels, word_ids):
    new_labels = []
    current_word_id = None

    for word_id in word_ids:
        if word_id is None:
            new_labels.append(-100)
        elif word_id != current_word_id:
            new_labels.append(label2id.get(labels[word_id], -100))
        else:
            new_labels.append(label2id.get(labels[word_id], -100))

        current_word_id = word_id

    return new_labels

def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True
    )
    all_labels = examples["tags"]
    new_labels = []
    for i, labels in enumerate(all_labels):
        word_ids = tokenized_inputs.word_ids(i)
        new_labels.append(align_labels_with_tokens(labels, word_ids))

    tokenized_inputs["labels"] = new_labels
    return tokenized_inputs


tokenized_datasets = dataset.map(
    tokenize_and_align_labels,
    batched=True,
    remove_columns=['tokens', 'tags'],
)

data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)
metric = evaluate.load("seqeval")

def compute_metrics(eval_preds):
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    true_labels = [[id2label.get(l, 'O') for l in label if l != -100] for label in labels]
    true_predictions = [
        [id2label.get(p, 'O') for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    all_metrics = metric.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": all_metrics["overall_precision"],
        "recall": all_metrics["overall_recall"],
        "f1": all_metrics["overall_f1"],
        "accuracy": all_metrics["overall_accuracy"],
    }

model = AutoModelForTokenClassification.from_pretrained(
    model_name,
    id2label=id2label,
    label2id=label2id,
)

def ensure_contiguous(tensor):
    return tensor.contiguous()

for name, param in model.named_parameters():
    param.data = ensure_contiguous(param.data)

args = TrainingArguments(
    output_dir="test-ner",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer,
)


trainer.train()


trainer.save_model("saved_model")
tokenizer.save_pretrained("saved_model")


loaded_model = AutoModelForTokenClassification.from_pretrained("saved_model")
loaded_tokenizer = AutoTokenizer.from_pretrained("saved_model")

