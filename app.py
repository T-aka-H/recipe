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
    """Hugging Face APIを使用して料理画像を生成"""
    try:
        hf_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        if not hf_api_key:
            print("ERROR: HUGGINGFACE_API_KEY not found in environment variables")
            return None

        print(f"Generating image for: {recipe_name} with ingredients: {ingredients}")

        # 日本料理に特化したプロンプト
        prompt = f"A beautiful, appetizing photo of {recipe_name}, Japanese home cooking dish, made with {', '.join(ingredients)}, professional food photography, natural soft lighting, wooden table, high resolution, realistic"
        print(f"Using prompt: {prompt}")
        
        headers = {
            'Authorization': f'Bearer {hf_api_key}',
        }
        
        # シンプルなデータ構造に変更
        data = {
            'inputs': prompt
        }
        
        # より信頼性の高いモデルを使用
        models_to_try = [
            'runwayml/stable-diffusion-v1-5',
            'CompVis/stable-diffusion-v1-4'
        ]
        
        for model in models_to_try:
            try:
                print(f"Trying model: {model}")
                response = requests.post(
                    f'https://api-inference.huggingface.co/models/{model}',
                    headers=headers, 
                    json=data, 
                    timeout=60
                )
                
                print(f"Response status code: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    # レスポンスがJSONかバイナリかチェック
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        # エラーレスポンスの場合
                        error_data = response.json()
                        print(f"API returned JSON error: {error_data}")
                        continue
                    else:
                        # 画像データの場合
                        image_data = base64.b64encode(response.content).decode('utf-8')
                        print(f"Successfully generated image, size: {len(response.content)} bytes")
                        return f"data:image/png;base64,{image_data}"
                        
                elif response.status_code == 503:
                    # モデルがロード中の場合
                    print(f"Model {model} is loading, trying next model...")
                    try:
                        error_info = response.json()
                        print(f"503 Error details: {error_info}")
                    except:
                        print(f"503 Error: {response.text}")
                    continue
                else:
                    print(f"Hugging Face API error with {model}: {response.status_code}")
                    try:
                        error_info = response.json()
                        print(f"Error details: {error_info}")
                    except:
                        print(f"Error text: {response.text}")
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"Timeout with model {model}, trying next...")
                continue
            except Exception as model_error:
                print(f"Exception with model {model}: {str(model_error)}")
                continue
        
        print("All models failed or are unavailable")
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

# 画像生成API（プレースホルダー版）
@app.route('/api/generate-image', methods=['POST'])
def generate_recipe_image():
    try:
        print("=== Image generation request received ===")
        data = request.json
        print(f"Request data: {data}")
        
        recipe_name = data.get('recipe_name')
        ingredients = data.get('ingredients', [])

        print(f"Recipe name: {recipe_name}")
        print(f"Ingredients: {ingredients}")

        if not recipe_name:
            print("ERROR: No recipe name provided")
            return jsonify({'error': 'レシピ名が必要です'}), 400

        # 料理の種類に応じたプレースホルダー画像を選択
        placeholder_images = {
            'default': [
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=512&h=512&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=512&h=512&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=512&h=512&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=512&h=512&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=512&h=512&fit=crop&auto=format"
            ],
            'rice': [
                "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=512&h=512&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=512&h=512&fit=crop&auto=format"
            ],
            'pasta': [
                "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=512&h=512&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1563379091339-03246963d51a?w=512&h=512&fit=crop&auto=format"
            ],
            'salad': [
                "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=512&h=512&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=512&h=512&fit=crop&auto=format"
            ]
        }
        
        # 料理名から画像カテゴリを推測
        recipe_lower = recipe_name.lower()
        if any(word in recipe_lower for word in ['ご飯', '米', 'rice', '丼', 'おにぎり']):
            category = 'rice'
        elif any(word in recipe_lower for word in ['パスタ', 'pasta', 'スパゲッティ', 'ペンネ']):
            category = 'pasta'
        elif any(word in recipe_lower for word in ['サラダ', 'salad', '野菜']):
            category = 'salad'
        else:
            category = 'default'
        
        import random
        image_url = random.choice(placeholder_images[category])
        
        print(f"Selected category: {category}")
        print(f"Using placeholder image: {image_url}")
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'recipe_name': recipe_name,
            'timestamp': datetime.now().isoformat(),
            'note': f'プレースホルダー画像を使用中 (カテゴリ: {category})'
        })

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