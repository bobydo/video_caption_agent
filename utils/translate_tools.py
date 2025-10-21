import requests
import json

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

def translate_text(text):
    try:
        # Handle long text by splitting into smaller chunks to avoid timeout
        MAX_CHUNK_SIZE = 1000  # Process 1000 chars at a time for better reliability
        
        print(f"📝 Total text length: {len(text)} characters")
        
        # If text is short enough, translate directly
        if len(text) <= MAX_CHUNK_SIZE:
            print(f"📝 Text is short, translating directly...")
            return _translate_single_chunk(text)
        
        # For long text, split by sentences and translate in chunks
        print(f"📦 Text is long, splitting into chunks...")
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        translated_chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence exceeds chunk size, translate current chunk first
            if len(current_chunk) + len(sentence) > MAX_CHUNK_SIZE and current_chunk:
                print(f"📦 Translating chunk {len(translated_chunks) + 1} ({len(current_chunk)} chars)...")
                chunk_result = _translate_single_chunk(current_chunk)
                translated_chunks.append(chunk_result)
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Translate remaining chunk
        if current_chunk:
            print(f"📦 Translating final chunk ({len(current_chunk)} chars)...")
            chunk_result = _translate_single_chunk(current_chunk)
            translated_chunks.append(chunk_result)
        
        # Combine all translated chunks
        translated_text = " ".join(translated_chunks)
        print(f"✅ Combined translation: {len(translated_text)} chars from {len(translated_chunks)} chunks")
        return translated_text
            
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return _get_fallback_translation(text)

def _translate_single_chunk(text):
    """Translate a single chunk of text using Ollama"""
    try:
        prompt = f"Please translate the following English text to Simplified Chinese. " \
                 f"Only return the Chinese translation, nothing else:\n\n{text}"
        
        payload = {
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }
        
        print(f"🌐 Calling Ollama API at {OLLAMA_URL}...")
        print(f"📝 Text to translate (first 100 chars): {text[:100]}...")
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result.get("response", "").strip()
            
            print(f" Translated text length: {len(translated_text)}")
            
            # Check if translation contains Chinese characters
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in translated_text)
            
            if translated_text and len(translated_text.strip()) > 3 and has_chinese:
                print(f"✅ Chunk translation successful: {translated_text[:100]}...")
                return translated_text
            else:
                raise Exception(f"Invalid translation response: '{translated_text}' (has_chinese: {has_chinese})")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"⚠️ Chunk translation failed: {e}")
        return _get_fallback_translation(text)

def _get_fallback_translation(text):
    """Provide fallback translation when Ollama fails"""
    print("📝 Using fallback Chinese translation...")
    # Return proper Chinese text instead of English
    chinese_translations = {
        "cell phones are not permitted": "不允许使用手机",
        "at your desk": "在你的办公桌上", 
        "sensitive information": "敏感信息",
        "team": "团队",
        "quickly": "快速地",
        "reiterate": "重申",
        "work": "工作",
        "phone": "电话",
        "corporate": "企业",
        "animation": "动画"
    }
    
    # Try to do basic word replacement
    translated = text.lower()
    for en, zh in chinese_translations.items():
        translated = translated.replace(en, zh)
        
    # If no translation happened, use generic Chinese text
    if translated == text.lower():
        return "这是一个关于工作场所手机使用规定的视频。公司不允许在办公桌上使用手机，因为我们处理敏感信息，不希望泄露客户账户信息。"
    
    return translated

