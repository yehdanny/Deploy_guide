"""
Step 1: Generate video script (prompts for Kling AI + metadata for YouTube)
Uses OpenAI API for script generation (or any compatible API)
"""
import json
import random
import os
import sys
from datetime import datetime

TOPICS_FILE = os.path.join(os.path.dirname(__file__), "topics.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

def load_topics():
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_topic(topics, used_file=None):
    """Pick a random topic, avoiding recently used ones."""
    used = []
    if used_file and os.path.exists(used_file):
        with open(used_file, "r", encoding="utf-8") as f:
            used = json.load(f)
    
    available = [i for i in range(len(topics)) if i not in used[-20:]]
    if not available:
        available = list(range(len(topics)))
        used = []
    
    idx = random.choice(available)
    used.append(idx)
    
    if used_file:
        with open(used_file, "w", encoding="utf-8") as f:
            json.dump(used, f)
    
    return topics[idx]

def generate_prompts(topic):
    """Generate 3 Kling video prompts for a 15-second short (3 x 5s segments)."""
    a = topic["species_a"]
    b = topic["species_b"]
    env = topic["environment"]
    
    prompts = [
        # Segment 1: Tension / encounter
        f"Cinematic wildlife footage, {env}, a {a} and a {b} face each other in tense standoff, "
        f"dramatic natural lighting, photorealistic, 4K quality, National Geographic style, "
        f"slight camera movement, dust particles in air, vertical 9:16 format",
        
        # Segment 2: Clash / action
        f"Cinematic wildlife footage, {env}, intense battle between a {a} and a {b}, "
        f"dynamic action shot, motion blur on fast movements, photorealistic, 4K quality, "
        f"dramatic angle, dust and debris, National Geographic style, vertical 9:16 format",
        
        # Segment 3: Aftermath / victor
        f"Cinematic wildlife footage, {env}, aftermath of battle between {a} and {b}, "
        f"the victor stands dominant, golden hour lighting, photorealistic, 4K quality, "
        f"epic wide shot transitioning to close-up, National Geographic style, vertical 9:16 format"
    ]
    
    return prompts

def generate_metadata(topic):
    """Generate YouTube metadata."""
    a = topic["species_a"]
    b = topic["species_b"]
    zh_a = topic["zh_a"]
    zh_b = topic["zh_b"]
    env = topic["environment"]
    
    title = f"{zh_a} vs {zh_b}！誰才是{env}的王者？ | {a} vs {b} #shorts"
    description = (
        f"🔥 {zh_a} vs {zh_b} — 自然界的終極對決！\n"
        f"在{env}中，這兩個物種展開了一場驚心動魄的鬥爭。\n"
        f"誰會勝出？看到最後！\n\n"
        f"🔥 {a} vs {b} — Ultimate showdown in the wild!\n"
        f"Watch this epic battle in the {env}.\n\n"
        f"#shorts #wildlife #animal #nature #vs #fight "
        f"#{a.replace(' ', '')} #{b.replace(' ', '')} "
        f"#動物 #野生動物 #自然 #{zh_a} #{zh_b}"
    )
    
    return {
        "title": title[:100],  # YouTube title limit
        "description": description,
        "tags": [a, b, "wildlife", "nature", "vs", "animal fight", "shorts",
                 zh_a, zh_b, "動物", "野生動物", "自然", "對決"]
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    topics = load_topics()
    used_file = os.path.join(OUTPUT_DIR, "used_topics.json")
    topic = pick_topic(topics, used_file)
    
    print(f"🎬 Selected topic: {topic['species_a']} vs {topic['species_b']}")
    print(f"   Environment: {topic['environment']}")
    
    prompts = generate_prompts(topic)
    metadata = generate_metadata(topic)
    
    # Create today's output folder
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_dir = os.path.join(OUTPUT_DIR, f"{date_str}_{topic['species_a']}_vs_{topic['species_b']}".replace(" ", "_"))
    os.makedirs(job_dir, exist_ok=True)
    
    job_data = {
        "topic": topic,
        "prompts": prompts,
        "metadata": metadata,
        "created_at": datetime.now().isoformat(),
        "status": "script_generated"
    }
    
    job_file = os.path.join(job_dir, "job.json")
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Script saved to: {job_file}")
    print(f"\n📝 Title: {metadata['title']}")
    print(f"\n🎥 Video prompts:")
    for i, p in enumerate(prompts, 1):
        print(f"   Segment {i}: {p[:80]}...")
    
    return job_dir

if __name__ == "__main__":
    result = main()
    print(f"\n📁 Job directory: {result}")
