# Classifier training (Person B)

Train in Google Colab (GPU): create `train_classifier.ipynb` here.
Base model `classla/bcms-bertic`, 5 labels (noise, patrol, accident, jam, clear),
data `data/labels_silver.jsonl` excluding ids in `data/gold_test.jsonl`.

After training, upload so others get it automatically:

    hf auth login
    hf upload <hf-username>/mapens-classifier models/classifier .

Then set `CLASSIFIER_REPO` in `.env.example` / `.env`.
