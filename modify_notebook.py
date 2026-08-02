import json

with open('./test/test_from_video.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell['cell_type'] == 'code':
        source = cell['source']
        source_str = "".join(source)
        
        if "import os\n" in source_str:
            if "import csv\n" not in source:
                cell['source'].insert(0, "import csv\n")
        
        if "while cap.isOpened():" in source_str:
            new_source = []
            for line in source:
                if line == "            fourcc = cv2.VideoWriter_fourcc(*'mp4v')\n":
                    new_source.append('            csv_path = os.path.join(output_dir, f"output_{os.path.splitext(file_name)[0]}.csv")\n')
                    new_source.append('            csv_file = open(csv_path, mode="w", newline="", encoding="utf-8")\n')
                    new_source.append('            csv_writer = csv.writer(csv_file)\n')
                    new_source.append('            csv_writer.writerow(["frame", "age", "gender", "score", "x", "y", "w", "h"])\n')
                    new_source.append(line)
                elif line == "                        # 1. 녹색 바운딩 박스 그리기\n":
                    new_source.append('                        # CSV에 데이터 기록\n')
                    new_source.append('                        csv_writer.writerow([frame_count, age, gender, round(score, 2), x, y, w, h])\n')
                    new_source.append('                        \n')
                    new_source.append(line)
                elif line == "            out.release()\n":
                    new_source.append(line)
                    new_source.append("            csv_file.close()\n")
                elif line == '            print(f"✅ 분석 완료! 결과 비디오 저장 위치: {output_path}\\n")\n':
                    new_source.append('            print(f"✅ 분석 완료! 결과 비디오 저장 위치: {output_path}")\n')
                    new_source.append('            print(f"✅ CSV 데이터 저장 위치: {csv_path}\\n")\n')
                else:
                    new_source.append(line)
            cell['source'] = new_source

with open('./test/test_from_video.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
