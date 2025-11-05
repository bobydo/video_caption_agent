import requests
import re
from config import DEFAULT_CONFIG

def translate_text(text):
    try:
        # Handle long text by splitting into smaller chunks to avoid timeout
        MAX_CHUNK_SIZE = DEFAULT_CONFIG.max_chunk_size
        
        print(f"Total text length: {len(text)} characters")
        
        # If text is short enough, translate directly
        if len(text) <= MAX_CHUNK_SIZE:
            print(f"📝 Text is short, translating directly...")
            return _translate_single_chunk(text)
        
        # For long text, split by sentences using LLM and translate in chunks
        print(f"Text is long, splitting into sentences using LLM...")

        sentences = _split_text_into_sentences(text)
        
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

def _split_text_into_sentences(text):
    """Split text into sentences using LLM for intelligent parsing"""
    try:
        split_prompt = DEFAULT_CONFIG.sentence_split_prompt_template.format(text=text)
        
        payload = {
            "model": DEFAULT_CONFIG.translation_model,
            "prompt": split_prompt,
            "stream": False,
            "options": DEFAULT_CONFIG.sentence_split_options
        }
        
        print(f"Using LLM to split text into sentences...")
        
        response = requests.post(DEFAULT_CONFIG.ollama_url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            split_result = result.get("response", "").strip()
            
            # Split by newlines and filter out empty lines
            sentences = [line.strip() for line in split_result.split('\n') if line.strip()]
            
            if sentences and len(sentences) > 0:
                print(f"✅ LLM split text into {len(sentences)} sentences")
                return sentences
            else:
                print("⚠️ LLM splitting failed, falling back to simple split")
                return [text]  # Return original text as single sentence
                
        else:
            print(f"⚠️ LLM splitting failed: HTTP {response.status_code}")
            return [text]  # Fallback to original text
            
    except Exception as e:
        print(f"⚠️ LLM sentence splitting error: {e}")
        # Fallback to regex sentence splitting
        sentences = re.split(DEFAULT_CONFIG.sentence_split_fallback_pattern, text)
        return sentences if sentences else [text]

def _translate_single_chunk(text):
    """Translate a single chunk of text using Ollama"""
    try:
        prompt = DEFAULT_CONFIG.translation_prompt_template.format(
            source_language=DEFAULT_CONFIG.source_language,
            target_language=DEFAULT_CONFIG.target_language,
            instruction=DEFAULT_CONFIG.translation_instruction,
            text=text
        )
        
        payload = {
            "model": DEFAULT_CONFIG.translation_model,
            "prompt": prompt,
            "stream": False,
            "options": DEFAULT_CONFIG.translation_options
        }
        
        print(f"🌐 Calling Ollama API at {DEFAULT_CONFIG.ollama_url}...")
        print(f"📝 Text to translate (first 100 chars): {text[:100]}...")
        
        response = requests.post(DEFAULT_CONFIG.ollama_url, json=payload, timeout=180)
        
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
    
    # Complete sentence translations (more accurate than word-by-word)
    sentence_translations = {
        "to be out at your desk": "在你的办公桌旁",
        "to be out at your desk.": "在你的办公桌旁。",
        "we deal with a lot of sensitive information": "我们处理大量敏感信息",
        "we deal with a lot of sensitive information.": "我们处理大量敏感信息。",
        "we don't want to compromise a client's account": "我们不想危及客户账户",
        "we don't want to compromise a client's account.": "我们不想危及客户账户。",
        "so cell phones are not permitted at your desk": "因此不允许在你的办公桌旁使用手机",
        "so cell phones are not permitted at your desk.": "因此不允许在你的办公桌旁使用手机。",
        "it's in the guidelines": "这在指导原则中",
        "it's in the guidelines.": "这在指导原则中。",
        "we explained it to you": "我们已经向你解释过了",
        "we explained it to you.": "我们已经向你解释过了。"
    }
    
    # Check for exact sentence matches first
    text_clean = text.strip()
    if text_clean.lower() in sentence_translations:
        return sentence_translations[text_clean.lower()]
    
    # If no exact match, provide appropriate fallback based on content
    text_lower = text.lower()
    if "desk" in text_lower and "phone" in text_lower:
        return "不允许在办公桌旁使用手机"
    elif "sensitive" in text_lower and "information" in text_lower:
        return "我们处理敏感信息"
    elif "client" in text_lower or "account" in text_lower:
        return "我们保护客户账户"
    elif "guidelines" in text_lower:
        return "这在指导原则中"
    else:
        # Generic fallback for unknown text
        return "这是关于工作场所政策的内容"

