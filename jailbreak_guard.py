from guardrails_ai.detect_jailbreak import DetectJailbreak


class CompatibleDetectJailbreak(DetectJailbreak):

    TEXT_CLASSIFIER_NAME = "your_file_path"
    def _predict_jailbreak(self, prompts):
        predictions = self.text_classifier(prompts)

        scores = []

        for pred in predictions:
            if pred["label"] == "LABEL_0":
                pred["label"] = 0
            elif pred["label"] == "LABEL_1":
                pred["label"] = 1

        for pred in predictions:
            old_score = pred["score"]

            is_safe = (
                pred["label"] == self.TEXT_CLASSIFIER_PASS_LABEL
            )

            assert (
                pred["label"]
                in {
                    self.TEXT_CLASSIFIER_PASS_LABEL,
                    self.TEXT_CLASSIFIER_FAIL_LABEL,
                }
                and 0.0 <= old_score <= 1.0
            )

            if is_safe:
                new_score = 0.5 - (old_score * 0.5)
            else:
                new_score = 0.5 + (old_score * 0.5)

            scores.append(
                self._rescale(
                    new_score,
                    *self.text_attack_scales
                )
            )

        return scores