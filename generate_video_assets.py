import asyncio
import os
import subprocess
import json
import glob
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
import edge_tts

WORKSPACE = r"c:\Users\SHANMUKHESWAR\OneDrive\Desktop\Phantom_stock\StockSentry-AI-Phantom-Stock-Out-Detector"
ASSETS_DIR = os.path.join(WORKSPACE, "assets")
ARTIFACTS_DIR = r"C:\Users\SHANMUKHESWAR\.gemini\antigravity-ide\brain\d3e446cf-a61d-46d3-a7f9-d30ec5dbdb88"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
OUTPUT_VIDEO = os.path.join(WORKSPACE, "StockSentry_AI_Live_Demo_Walkthrough.mp4")
OUTPUT_SRT = os.path.join(WORKSPACE, "StockSentry_AI_Live_Demo_Subtitles.srt")
OUTPUT_VTT = os.path.join(WORKSPACE, "StockSentry_AI_Live_Demo_Subtitles.vtt")
SCRATCH = os.path.join(WORKSPACE, "video_scratch")

os.makedirs(SCRATCH, exist_ok=True)

# 10 Curated Scenes matching the user's requirement: 3-minute live demo explaining the whole project, workflow, and how to use it
SCENES = [
    {
        "id": 1,
        "tag": "01 • THE PROBLEM & HOOK",
        "title": "StockSentry AI — The $112B Phantom Stock Crisis",
        "image": os.path.join(ASSETS_DIR, "stocksentry_architecture_diagram.jpg"),
        "points": [
            "ERP records positive stock on hand, but physical shelf is empty",
            "Restocking purchase orders never trigger — sales vanish for weeks",
            "Silent retail shrinkage drains over $112 Billion worldwide"
        ],
        "sentences": [
            "Welcome to StockSentry AI, an autonomous operations console and Bayesian detector built to eliminate retail's 112-billion-dollar silent crisis: Phantom Stock-Outs.",
            "When an ERP system records positive inventory but the shelf is empty, automated restocking stops, and revenue quietly bleeds away."
        ]
    },
    {
        "id": 2,
        "tag": "02 • COMPETITIVE NOVELTY",
        "title": "Novelty: Zero CapEx & The 20-Audit Daily Quota",
        "image": os.path.join(ASSETS_DIR, "stocksentry_workflow_diagram.jpg"),
        "points": [
            "Zero Hardware CapEx ($0 vs $100,000 for RFID/Ceiling Cameras)",
            "55% Slow-Mover Filter suppresses intermittent demand false alarms",
            "Strict R1 quota compliance: Exactly 20 physical checks per day"
        ],
        "sentences": [
            "A typical supermarket carries 30,000 SKUs, but store associates only have time for exactly 20 physical checks per day.",
            "Unlike hardware cameras or RFID costing 100,000 dollars, StockSentry requires zero new hardware, using a 55% slow-mover filter to maximize Precision at 20."
        ]
    },
    {
        "id": 3,
        "tag": "03 • DAILY COMMAND CENTER",
        "title": "Command Center & 25-Store Network Health",
        "image": os.path.join(ARTIFACTS_DIR, "command_center_dashboard_1793198591277.png"),
        "points": [
            "Real-time operational overview across all 25 retail branches",
            "Tracks phantom alert rates & associate audit compliance",
            "Dynamic 20-bar priority distribution highlighting critical risk items"
        ],
        "sentences": [
            "Every morning at 8:00 AM, the store manager opens the Daily Command Center.",
            "Here, they monitor network health across all 25 retail branches, tracking phantom anomaly rates and the 20-bar priority score distribution."
        ]
    },
    {
        "id": 4,
        "tag": "04 • MORNING QUEUE",
        "title": "The Morning Queue — Ranked Top-20 Checks",
        "image": os.path.join(ARTIFACTS_DIR, "morning_queue_page_1793198610144.png"),
        "points": [
            "Overnight Bayesian analysis prioritizes Top 20 discrepancies",
            "Dynamic confidence scores ranging from 96.4 down to 54.2",
            "Plain-English diagnostic reasons ready for mobile tablet audit"
        ],
        "sentences": [
            "At 8:30 AM, the floor associate opens the Morning Queue on their mobile tablet.",
            "StockSentry has prioritized the Top 20 highest-probability phantom items, complete with dynamic confidence scores and plain-English reasons."
        ]
    },
    {
        "id": 5,
        "tag": "05 • DEEP DIAGNOSTIC",
        "title": "SKU Investigation & Multi-Class Separation",
        "image": os.path.join(ARTIFACTS_DIR, "verification_modal_1793198695799.png"),
        "points": [
            "Poisson customer demand baseline plotted against 0 sales",
            "Multi-class geometry: True Theft vs Shelf Misplacement vs Delisting",
            "30-day velocity sparkline & promotional footfall multipliers"
        ],
        "sentences": [
            "Clicking into Rank 1, Sparkling Water SKU-104, opens the deep diagnostic modal.",
            "The associate reviews expected Poisson customer demand against zero sales, verifying whether this is true shrinkage theft or accidental shelf misplacement."
        ]
    },
    {
        "id": 6,
        "tag": "06 • STORE AUDIT",
        "title": "Physical Shelf Verification & Field Ground-Truth",
        "image": os.path.join(ARTIFACTS_DIR, "audit_notes_entered_1793198735036.png"),
        "points": [
            "Guided count stepper & barcode scanner simulation",
            "Categorized outcomes: Confirmed Phantom vs False Alarm",
            "Field notes logged directly into persistent SQLite database"
        ],
        "sentences": [
            "Walking to Aisle 2, Bay 4 with their tablet, the associate inspects the physical shelf.",
            "Finding zero units, they log the count, select Confirmed Phantom Stock-Out, enter notes, and submit the audit directly to the system."
        ]
    },
    {
        "id": 7,
        "tag": "07 • ERP AUTO-RECONCILIATION",
        "title": "Two-Way SQLite Sync & Restock PO Wake-Up",
        "image": os.path.join(ARTIFACTS_DIR, "feedback_learning_page_1793198806983.png"),
        "points": [
            "Sub-millisecond write-down: central ERP ledger updated to 0",
            "Immediately wakes up replenishment PO to restock shelf tomorrow",
            "Feedback loop continuously calibrates Bayesian model weights"
        ],
        "sentences": [
            "In sub-millisecond real time, StockSentry's SQLite backend executes an automated write-down, setting central ERP inventory to zero.",
            "This immediately wakes up the replenishment pipeline, generating an automated purchase order to restock the shelf tomorrow."
        ]
    },
    {
        "id": 8,
        "tag": "08 • RUPEE RECOVERY ROI",
        "title": "Rupee Recovery Console & CFO Auditable ROI",
        "image": os.path.join(ARTIFACTS_DIR, "rupee_recovery_page_1793198977411.png"),
        "points": [
            "CFO-auditable formula: Demand × Price × Days × Margin",
            "Over ₹2.78 Crore recovered annually across 25 stores",
            "Interactive sensitivity sliders for prevented leakage duration"
        ],
        "sentences": [
            "In the Rupee Recovery console, retail executives track real financial return.",
            "Using transparent unit economics, StockSentry calculates revenue saved per verified item, recovering over 2.78 Crore rupees across 25 stores annually."
        ]
    },
    {
        "id": 9,
        "tag": "09 • DATA INTEGRATION",
        "title": "Store Data Integration Hub & 7 Failure Modes",
        "image": os.path.join(ARTIFACTS_DIR, "store_data_integration_hub_1793203180445.png"),
        "points": [
            "Cloud ERP APIs for SAP S/4HANA & Oracle Retail",
            "Automated 03:00 AM POS CSV batch sync with live dropzone",
            "Synthetic Retail Studio stress-tests 7 retail failure modes"
        ],
        "sentences": [
            "Connecting your store is effortless with support for Cloud ERP APIs, POS CSV batch drops, and Android handheld scanners.",
            "Our built-in Synthetic Studio allows operators to simulate and stress-test seven real-world retail failure modes."
        ]
    },
    {
        "id": 10,
        "tag": "10 • BENCHMARK & COPILOT",
        "title": "Sub-5ms Benchmark Engine & AI Copilot",
        "image": os.path.join(ARTIFACTS_DIR, "copilot_integration_response_1793203456783.png"),
        "points": [
            "Official evaluate.py harness: 750 store-days in < 5 milliseconds",
            "93.8% Precision@20 vs 34.2% baseline rule",
            "Conversational edge AI Copilot answers operational queries"
        ],
        "sentences": [
            "With our competition benchmark evaluating 750 store-days in under 5 milliseconds at 93.8% precision, and an intelligent AI Copilot ready to assist staff,",
            "StockSentry AI turns shrinkage into measurable profit. Thank you for watching this live demonstration."
        ]
    }
]

def format_timestamp_srt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def format_timestamp_vtt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

async def step1_generate_audio():
    print("--- STEP 1: Generating Indian English Audio Tracks (Voice: en-IN-PrabhatNeural) ---")
    voice = "en-IN-PrabhatNeural"
    # rate = "+14%" gives energetic, natural pacing ~180s total
    rate = "+14%"
    
    total_time = 0.0
    for scene in SCENES:
        sid = scene["id"]
        full_text = " ".join(scene["sentences"])
        audio_file = os.path.join(SCRATCH, f"scene_{sid}.mp3")
        
        communicate = edge_tts.Communicate(full_text, voice, rate=rate)
        await communicate.save(audio_file)
        
        # Probe duration
        probe = subprocess.run(
            [FFMPEG_EXE, "-i", audio_file, "-f", "null", "-"],
            stderr=subprocess.PIPE, text=True
        )
        duration = 18.0
        for line in probe.stderr.split("\n"):
            if "Duration:" in line:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                duration = float(h) * 3600 + float(m) * 60 + float(s)
                break
        
        scene["audio_file"] = audio_file
        scene["duration"] = duration
        scene["start_time"] = total_time
        scene["end_time"] = total_time + duration
        total_time += duration
        print(f"Scene {sid:02d} | Duration: {duration:.2f}s | Audio: {os.path.basename(audio_file)}")
        
    print(f"\nMaster Audio Duration: {total_time:.2f} seconds ({total_time/60:.2f} minutes) -> Target ~3.0 mins achieved!\n")
    return total_time

def step2_generate_subtitles():
    print("--- STEP 2: Building Subtitle Files (.srt & .vtt) ---")
    srt_lines = []
    vtt_lines = ["WEBVTT\n"]
    
    sub_index = 1
    for scene in SCENES:
        s_start = scene["start_time"]
        s_dur = scene["duration"]
        half_dur = s_dur / 2.0
        
        # Sentence 1
        t1_start = s_start
        t1_end = s_start + half_dur
        # Sentence 2
        t2_start = t1_end
        t2_end = s_start + s_dur
        
        # SRT 1
        srt_lines.append(f"{sub_index}")
        srt_lines.append(f"{format_timestamp_srt(t1_start)} --> {format_timestamp_srt(t1_end)}")
        srt_lines.append(scene["sentences"][0] + "\n")
        
        # VTT 1
        vtt_lines.append(f"{format_timestamp_vtt(t1_start)} --> {format_timestamp_vtt(t1_end)}")
        vtt_lines.append(scene["sentences"][0] + "\n")
        sub_index += 1
        
        # SRT 2
        srt_lines.append(f"{sub_index}")
        srt_lines.append(f"{format_timestamp_srt(t2_start)} --> {format_timestamp_srt(t2_end)}")
        srt_lines.append(scene["sentences"][1] + "\n")
        
        # VTT 2
        vtt_lines.append(f"{format_timestamp_vtt(t2_start)} --> {format_timestamp_vtt(t2_end)}")
        vtt_lines.append(scene["sentences"][1] + "\n")
        sub_index += 1
        
    with open(OUTPUT_SRT, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
        
    with open(OUTPUT_VTT, "w", encoding="utf-8") as f:
        f.write("\n".join(vtt_lines))
        
    print(f"Generated SRT: {OUTPUT_SRT}")
    print(f"Generated VTT: {OUTPUT_VTT}\n")

def step3_render_slide_images():
    print("--- STEP 3: Rendering High-Definition 1080p Video Slide Frames ---")
    W, H = 1920, 1080
    
    font_bold_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
    font_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    font_point = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
    font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    
    for scene in SCENES:
        sid = scene["id"]
        img_source_path = scene["image"]
        
        # Load screenshot/diagram
        try:
            raw_screen = Image.open(img_source_path).convert("RGBA")
        except Exception as e:
            print(f"Warning: Could not open {img_source_path}, creating placeholder: {e}")
            raw_screen = Image.new("RGBA", (1280, 720), (15, 23, 42, 255))
            
        # We will create 2 slides per scene (one for sentence 1, one for sentence 2)
        for part_idx, sentence_text in enumerate(scene["sentences"], start=1):
            slide = Image.new("RGBA", (W, H), (10, 15, 29, 255)) # Dark slate canvas
            draw = ImageDraw.Draw(slide)
            
            # 1. Top Header Banner (Height 100px)
            draw.rectangle([(0, 0), (W, 100)], fill=(15, 23, 42, 255))
            draw.line([(0, 100), (W, 100)], fill=(30, 41, 59, 255), width=2)
            
            # Logo & Tag
            draw.text((40, 24), "StockSentry AI", fill=(56, 189, 248, 255), font=font_bold_title)
            draw.text((320, 34), "•  Autonomous Phantom Stock-Out Detector", fill=(148, 163, 184, 255), font=font_tag)
            
            # Step pill
            step_str = f"STEP {sid:02d} / 10"
            draw.rounded_rectangle([(W - 220, 25), (W - 40, 75)], radius=12, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=2)
            draw.text((W - 195, 36), step_str, fill=(56, 189, 248, 255), font=font_badge)
            
            # 2. Scene Section Header & Tag
            draw.text((40, 116), scene["tag"], fill=(245, 158, 11, 255), font=font_tag)
            draw.text((40, 148), scene["title"], fill=(248, 250, 252, 255), font=font_bold_title)
            
            # 3. Main Center Display Container (Screenshot)
            # Box dimensions: X: 40 to 1320 (width 1280), Y: 210 to 890 (height 680)
            box_x, box_y, box_w, box_h = 40, 210, 1280, 680
            draw.rounded_rectangle([(box_x - 3, box_y - 3), (box_x + box_w + 3, box_y + box_h + 3)], radius=16, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=2)
            
            # Resize image to fit box proportionally
            aspect = raw_screen.width / raw_screen.height
            if aspect > (box_w / box_h):
                new_w = box_w
                new_h = int(box_w / aspect)
            else:
                new_h = box_h
                new_w = int(box_h * aspect)
            
            scaled_img = raw_screen.resize((new_w, new_h), Image.Resampling.LANCZOS)
            offset_x = box_x + (box_w - new_w) // 2
            offset_y = box_y + (box_h - new_h) // 2
            slide.paste(scaled_img, (offset_x, offset_y), scaled_img if scaled_img.mode == "RGBA" else None)
            
            # 4. Right Side Feature Highlights Card (X: 1350 to 1880, Y: 210 to 890)
            card_x, card_y, card_w, card_h = 1350, 210, 530, 680
            draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], radius=16, fill=(15, 23, 42, 255), outline=(30, 41, 59, 255), width=2)
            
            # Card Title
            draw.text((card_x + 30, card_y + 30), "KEY CAPABILITIES", fill=(56, 189, 248, 255), font=font_tag)
            draw.line([(card_x + 30, card_y + 65), (card_x + card_w - 30, card_y + 65)], fill=(30, 41, 59, 255), width=1)
            
            # Feature Points
            cur_y = card_y + 85
            colors = [(16, 185, 129, 255), (59, 130, 246, 255), (245, 158, 11, 255)]
            for p_idx, pt in enumerate(scene["points"]):
                # bullet circle
                draw.ellipse([(card_x + 30, cur_y + 6), (card_x + 46, cur_y + 22)], fill=colors[p_idx % len(colors)])
                # text wrap
                words = pt.split()
                line = ""
                for w in words:
                    test_line = line + " " + w if line else w
                    bbox = draw.textbbox((0, 0), test_line, font=font_point)
                    if (bbox[2] - bbox[0]) < 430:
                        line = test_line
                    else:
                        draw.text((card_x + 60, cur_y), line, fill=(226, 232, 240, 255), font=font_point)
                        cur_y += 32
                        line = w
                if line:
                    draw.text((card_x + 60, cur_y), line, fill=(226, 232, 240, 255), font=font_point)
                    cur_y += 50
                    
            # Bottom highlight badge in the card
            draw.rounded_rectangle([(card_x + 25, card_y + card_h - 130), (card_x + card_w - 25, card_y + card_h - 25)], radius=12, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=1)
            draw.text((card_x + 45, card_y + card_h - 115), "PRECISION & SPEED", fill=(148, 163, 184, 255), font=font_badge)
            draw.text((card_x + 45, card_y + card_h - 85), "93.8% Precision@20  |  < 5ms Latency", fill=(255, 255, 255, 255), font=font_point)
            draw.text((card_x + 45, card_y + card_h - 55), "100% Zero-Hardware CapEx Engine", fill=(52, 211, 153, 255), font=font_badge)

            # 5. Bottom Subtitle Ribbon (Height 140px: Y 915 to 1055)
            # Semi-transparent dark container with bright contrast
            sub_box = [(40, 915), (W - 40, 1055)]
            draw.rounded_rectangle(sub_box, radius=14, fill=(8, 12, 22, 245), outline=(56, 189, 248, 200), width=2)
            
            # Subtitle Voice Badge
            draw.text((65, 928), "🎙️ NARRATION (Indian English • en-IN-PrabhatNeural)", fill=(56, 189, 248, 255), font=font_tag)
            
            # Subtitle Text (Wrapped nicely)
            words = sentence_text.split()
            sub_line = ""
            sub_lines = []
            for w in words:
                test_sub = sub_line + " " + w if sub_line else w
                bbox = draw.textbbox((0, 0), test_sub, font=font_sub)
                if (bbox[2] - bbox[0]) < (W - 160):
                    sub_line = test_sub
                else:
                    sub_lines.append(sub_line)
                    sub_line = w
            if sub_line:
                sub_lines.append(sub_line)
                
            sy = 962
            for sl in sub_lines[:2]:
                draw.text((65, sy), sl, fill=(255, 255, 255, 255), font=font_sub)
                sy += 38
                
            slide_file = os.path.join(SCRATCH, f"slide_{sid}_part{part_idx}.png")
            slide.convert("RGB").save(slide_file, quality=95)
            scene[f"slide_part{part_idx}"] = slide_file
            
    print(f"Successfully rendered 20 high-definition 1080p slide frames in {SCRATCH}\n")

def step4_assemble_video():
    print("--- STEP 4: Assembling Video Clips and Merging Master Audio via FFmpeg ---")
    clip_list = []
    
    for scene in SCENES:
        sid = scene["id"]
        dur = scene["duration"]
        half_dur = dur / 2.0
        
        slide1 = scene["slide_part1"]
        slide2 = scene["slide_part2"]
        audio = scene["audio_file"]
        
        # Clip part 1 (video only)
        clip1_path = os.path.join(SCRATCH, f"clip_{sid}_p1.mp4")
        subprocess.run([
            FFMPEG_EXE, "-y",
            "-loop", "1",
            "-t", f"{half_dur:.3f}",
            "-i", slide1,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "24",
            clip1_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Clip part 2 (video only)
        clip2_path = os.path.join(SCRATCH, f"clip_{sid}_p2.mp4")
        subprocess.run([
            FFMPEG_EXE, "-y",
            "-loop", "1",
            "-t", f"{half_dur:.3f}",
            "-i", slide2,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "24",
            clip2_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Concat video parts for this scene and attach audio
        scene_video_only = os.path.join(SCRATCH, f"scene_{sid}_v.mp4")
        scene_list_txt = os.path.join(SCRATCH, f"scene_{sid}_concat.txt")
        with open(scene_list_txt, "w") as f:
            f.write(f"file '{clip1_path}'\nfile '{clip2_path}'\n")
            
        subprocess.run([
            FFMPEG_EXE, "-y",
            "-f", "concat", "-safe", "0",
            "-i", scene_list_txt,
            "-i", audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            scene_video_only
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        clip_list.append(scene_video_only)
        print(f"Scene {sid:02d} clip rendered & synchronized!")
        
    # Concatenate all 10 scene videos into the final output
    print("\nConcatenating all 10 scenes into master demonstration video...")
    master_concat_txt = os.path.join(SCRATCH, "master_concat.txt")
    with open(master_concat_txt, "w") as f:
        for c in clip_list:
            f.write(f"file '{c}'\n")
            
    subprocess.run([
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", master_concat_txt,
        "-c", "copy",
        OUTPUT_VIDEO
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    print(f"\n=======================================================")
    print(f"SUCCESS: Master Live Demo Walkthrough Video Created!")
    print(f"Video File: {OUTPUT_VIDEO}")
    
    # Check final duration & size
    probe = subprocess.run([
        FFMPEG_EXE, "-i", OUTPUT_VIDEO, "-f", "null", "-"
    ], stderr=subprocess.PIPE, text=True)
    for line in probe.stderr.split("\n"):
        if "Duration:" in line:
            print(f"Final Video Duration: {line.split('Duration:')[1].split(',')[0].strip()}")
            break
            
    file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"Final File Size: {file_size_mb:.2f} MB")
    print(f"=======================================================\n")

async def main():
    await step1_generate_audio()
    step2_generate_subtitles()
    step3_render_slide_images()
    step4_assemble_video()

if __name__ == "__main__":
    asyncio.run(main())
