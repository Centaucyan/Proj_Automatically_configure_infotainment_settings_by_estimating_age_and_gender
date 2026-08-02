# Proj_Automatically_configure_infotainment_settings_by_estimating_age_and_gender

* Update: 2026.07.29.
## 1. Description
* 사람 얼굴 영상으로부터 성별과 나이를 추측하여 안내 멘트의 발음 속도와 볼륨을 조절
* 적용 가능 분야: ADAS(DMS)_운전자의 성별과 나이를 추측하여 차량의 인포테인먼트를 설정함
* Base model: DeepFace(https://github.com/serengil/deepface.git)
---

## 2. Environment
* **OS:** Ubuntu 22.04 LTS(Jammy Jellyfish)
* **Language:** Python(ver: 3.12. conda 가상환경)
---

## 3. Pre-installation
```bash
python -m pip install jinja2 pyyaml typeguard matplotlib

#. deepface 폴더로 이동
cd Proj_Age_and_gender_estimation_based_on_facial_images/ai_model/deepface/

python -m pip install -e .

python -m pip install tf-keras
```
---

## 4. Execute Commands
```bash

```
---