from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from datetime import datetime
import requests
import base64
from io import BytesIO

app = Flask(__name__)

# ★ Gemini APIキー設定（環境変数から）
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# ★ Geminiモデル定義（1.5 Flashを使用）
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 気分一覧
MOODS = [
    {"id": "salty", "name": "塩味のもの", "emoji": "🧂"},
    {"id": "spicy", "name": "からいもの", "emoji": "🌶️"},
    {"id": "sweet", "name": "甘めのもの", "emoji": "🍯"},
    {"id": "energizing", "name": "元気がでるもの", "emoji": "💪"},
    {"id": "light", "name": "軽いもの", "emoji": "🥗"},
    {"id": "gentle", "name": "胃にやさしいもの", "emoji": "☕"}
]

# 食材リスト
INGREDIENTS = [
    {"id": "rice", "name": "お米", "category": "主食"},
    {"id": "pasta", "name": "パスタ", "category": "主食"},
    {"id": "bread", "name": "パン", "category": "主食"},
    {"id": "udon", "name": "うどん", "category": "主食"},
    {"id": "soba", "name": "そば", "category": "主食"},
    {"id": "chicken", "name": "鶏肉", "category": "肉類"},
    {"id": "pork", "name": "豚肉", "category": "肉類"},
    {"id": "beef", "name": "牛肉", "category": "肉類"},
    {"id": "ground_meat", "name": "ひき肉", "category": "肉類"},
    {"id": "salmon", "name": "鮭", "category": "魚類"},
    {"id": "tuna", "name": "まぐろ", "category": "魚類"},
    {"id": "shrimp", "name": "えび", "category": "魚類"},
    {"id": "egg", "name": "卵", "category": "卵・乳製品"},
    {"id": "milk", "name": "牛乳", "category": "卵・乳製品"},
    {"id": "cheese", "name": "チーズ", "category": "卵・乳製品"},
    {"id": "tofu", "name": "豆腐", "category": "大豆製品"},
    {"id": "natto", "name": "納豆", "category": "大豆製品"},
    {"id": "onion", "name": "玉ねぎ", "category": "野菜"},
    {"id": "carrot", "name": "にんじん", "category": "野菜"},
    {"id": "potato", "name": "じゃがいも", "category": "野菜"},
    {"id": "cabbage", "name": "キャベツ", "category": "野菜"},
    {"id": "tomato", "name": "トマト", "category": "野菜"},
    {"id": "cucumber", "name": "きゅうり", "category": "野菜"},
    {"id": "lettuce", "name": "レタス", "category": "野菜"},
    {"id": "spinach", "name": "ほうれん草", "category": "野菜"},
    {"id": "mushroom", "name": "きのこ類", "category": "野菜"},
    {"id": "bell_pepper", "name": "ピーマン", "category": "野菜"},
    {"id": "banana", "name": "バナナ", "category": "果物"},
    {"id": "apple", "name": "りんご", "category": "果物"},
    {"id": "lemon", "name": "レモン", "category": "果物"}
]



def generate_food_image_huggingface(recipe_name, ingredients):
    """Hugging Face APIを使用して料理画像を生成（2025年版）"""
    try:
        hf_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        if not hf_api_key:
            print("ERROR: HUGGINGFACE_API_KEY not found in environment variables")
            return None

        print(f"Generating AI image for: {recipe_name} with ingredients: {ingredients}")

        # より詳細で効果的なプロンプト
        prompt = f"A delicious, appetizing photo of {recipe_name}, Japanese home cooking, beautifully plated dish with {', '.join(ingredients)}, professional food photography, natural lighting, high quality, realistic, detailed"
        print(f"Using prompt: {prompt}")
        
        headers = {
            'Authorization': f'Bearer {hf_api_key}',
            'Content-Type': 'application/json'
        }
        
        # 2025年に利用可能なモデルを使用
        models_to_try = [
            'black-forest-labs/FLUX.1-schnell',  # 2024年の人気モデル
            'stabilityai/stable-diffusion-xl-base-1.0',  # SDXL
            'runwayml/stable-diffusion-v1-5',
            'prompthero/openjourney-v4',  # 代替モデル
            'dreamlike-art/dreamlike-photoreal-2.0'  # フォトリアル特化
        ]
        
        for model in models_to_try:
            try:
                print(f"Trying model: {model}")
                
                # モデルによってパラメータを調整
                if 'FLUX' in model:
                    data = {
                        "inputs": prompt,
                        "parameters": {
                            "guidance_scale": 3.5,
                            "num_inference_steps": 4,
                            "max_sequence_length": 256
                        }
                    }
                elif 'xl' in model.lower():
                    data = {
                        "inputs": prompt,
                        "parameters": {
                            "guidance_scale": 7.5,
                            "num_inference_steps": 20,
                            "width": 512,
                            "height": 512
                        }
                    }
                else:
                    data = {
                        "inputs": prompt,
                        "parameters": {
                            "guidance_scale": 7.5,
                            "num_inference_steps": 25
                        }
                    }
                
                response = requests.post(
                    f'https://api-inference.huggingface.co/models/{model}',
                    headers=headers, 
                    json=data, 
                    timeout=120
                )
                
                print(f"Response status code: {response.status_code}")
                
                if response.status_code == 200:
                    # レスポンスタイプをチェック
                    content_type = response.headers.get('content-type', '')
                    print(f"Content type: {content_type}")
                    
                    if 'application/json' in content_type:
                        # エラーレスポンスかもしれない
                        try:
                            error_data = response.json()
                            print(f"JSON response: {error_data}")
                            
                            # モデルがロード中の場合
                            if 'loading' in str(error_data).lower():
                                print(f"Model {model} is still loading, trying next...")
                                continue
                            else:
                                print(f"Model {model} returned error: {error_data}")
                                continue
                        except:
                            print(f"Failed to parse JSON response from {model}")
                            continue
                    else:
                        # バイナリ画像データの場合
                        if len(response.content) > 1000:  # 有効な画像データかチェック
                            image_data = base64.b64encode(response.content).decode('utf-8')
                            print(f"Successfully generated image with {model}, size: {len(response.content)} bytes")
                            return f"data:image/png;base64,{image_data}"
                        else:
                            print(f"Response too small from {model}: {len(response.content)} bytes")
                            continue
                            
                elif response.status_code == 503:
                    print(f"Model {model} is loading (503), trying next...")
                    continue
                elif response.status_code == 401:
                    print(f"Authentication error (401) - check API key")
                    return None
                elif response.status_code == 404:
                    print(f"Model {model} not found (404), trying next...")
                    continue
                else:
                    print(f"HTTP {response.status_code} error with {model}: {response.text}")
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"Timeout with model {model}, trying next...")
                continue
            except Exception as model_error:
                print(f"Exception with model {model}: {str(model_error)}")
                continue
        
        print("All AI models failed or are unavailable")
        return None
            
    except Exception as e:
        print(f"Hugging Face画像生成エラー: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

# ルートページ
@app.route('/')
def index():
    return render_template('index.html', moods=MOODS, ingredients=INGREDIENTS)

# レシピ生成API
@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    try:
        data = request.json
        mood = data.get('mood')
        selected_ingredients = data.get('ingredients', [])

        if not mood or not selected_ingredients:
            return jsonify({'error': '気分と食材を選択してください'}), 400

        ingredient_names = [
            next((i['name'] for i in INGREDIENTS if i['id'] == ingredient_id), ingredient_id)
            for ingredient_id in selected_ingredients
        ]
        mood_name = next((m['name'] for m in MOODS if m['id'] == mood), mood)

        prompt = f"""
あなたは経験豊富な日本の家庭料理の料理人です。
以下の条件に基づいて、5つの料理レシピを提案してください。

【気分・好み】: {mood_name}
【使用可能な食材】: {', '.join(ingredient_names)}

以下の形式で5つのレシピを提案してください：

1. **料理名**
   - 調理時間: XX分
   - 難易度: ★☆☆（3段階）
   - 材料: 使用する食材を列挙
   - 作り方: 3〜5ステップで簡潔に
   - ポイント: 美味しく作るコツ

※注意:
- 選択された食材はなるべくすべて使用してください。
- 気分に合った味付け・調理法を選んでください。
- 一般的な調味料（醤油・塩・胡椒など）は使用可能。
- 初心者でも作れるレシピを心がけてください。
"""

        response = model.generate_content(prompt)
        return jsonify({
            'success': True,
            'mood': mood_name,
            'ingredients': ingredient_names,
            'recipes': response.text,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'レシピ生成中にエラーが発生しました: {str(e)}'}), 500

# AI画像生成API
@app.route('/api/generate-image', methods=['POST'])
def generate_recipe_image():
    try:
        print("=== AI Image generation request received ===")
        data = request.json
        print(f"Request data: {data}")
        
        recipe_name = data.get('recipe_name')
        ingredients = data.get('ingredients', [])

        print(f"Recipe name: {recipe_name}")
        print(f"Ingredients: {ingredients}")

        if not recipe_name:
            print("ERROR: No recipe name provided")
            return jsonify({'error': 'レシピ名が必要です'}), 400

        # 環境変数チェック
        hf_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        print(f"HF API Key present: {bool(hf_api_key)}")
        if hf_api_key:
            print(f"HF API Key starts with: {hf_api_key[:10]}...")

        # AI画像生成を実行
        if hf_api_key:
            print("Attempting AI image generation with Hugging Face...")
            image_url = generate_food_image_huggingface(recipe_name, ingredients)
            print(f"AI image generation result: {bool(image_url)}")
            
            if image_url:
                print("SUCCESS: AI image generated successfully")
                return jsonify({
                    'success': True,
                    'image_url': image_url,
                    'recipe_name': recipe_name,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'AI Generated'
                })
            else:
                # AI生成失敗時はプレースホルダーにフォールバック
                print("AI generation failed, falling back to placeholder...")
                placeholder_images = [
                    "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=512&h=512&fit=crop&auto=format",
                    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=512&h=512&fit=crop&auto=format",
                    "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=512&h=512&fit=crop&auto=format"
                ]
                import random
                fallback_image = random.choice(placeholder_images)
                
                return jsonify({
                    'success': True,
                    'image_url': fallback_image,
                    'recipe_name': recipe_name,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'Fallback (AI generation temporarily unavailable)',
                    'note': 'AI画像生成が一時的に利用できないため、代替画像を表示しています'
                })
        else:
            print("ERROR: HUGGINGFACE_API_KEY not found")
            return jsonify({
                'success': False,
                'error': 'HUGGINGFACE_API_KEYが設定されていません。環境変数を確認してください。'
            }), 500

    except Exception as e:
        print(f"EXCEPTION in generate_recipe_image: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': f'画像生成中にエラーが発生しました: {str(e)}'}), 500

# ヘルスチェック用
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# 実行
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)