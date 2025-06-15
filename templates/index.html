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
    {"id": "happy", "name": "元気いっぱい", "emoji": "😄"},
    {"id": "tired", "name": "疲れ気味", "emoji": "😴"},
    {"id": "healthy", "name": "ヘルシー志向", "emoji": "🥗"},
    {"id": "comfort", "name": "家庭的な気分", "emoji": "🏠"},
    {"id": "adventure", "name": "冒険したい", "emoji": "🌟"},
    {"id": "spicy", "name": "スパイシー", "emoji": "🌶️"}
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
    """Hugging Face新しいInference Providersを使用して料理画像を生成"""
    try:
        hf_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        if not hf_api_key:
            print("ERROR: HUGGINGFACE_API_KEY not found in environment variables")
            return None

        print(f"Generating AI image for: {recipe_name} with ingredients: {ingredients}")

        # 日本語を英語に翻訳してAIが理解しやすくする
        recipe_translations = {
            "ピーマンの塩ダレ焼き": "Grilled green peppers with salt sauce",
            "親子丼": "Chicken and egg rice bowl (oyakodon)",
            "きのこの塩焼きおにぎり": "Grilled mushroom rice balls with salt",
            "チャーハン": "Fried rice",
            "オムライス": "Omurice (fried rice wrapped in omelet)",
            "焼きそば": "Yakisoba noodles",
            "唐揚げ": "Japanese fried chicken (karaage)",
            "生姜焼き": "Ginger pork stir-fry",
            "麻婆豆腐": "Mapo tofu",
            "肉じゃが": "Nikujaga (Japanese beef and potato stew)",
            "野菜炒め": "Stir-fried vegetables"
        }
        
        # 料理名を英語に変換
        english_recipe = recipe_translations.get(recipe_name, recipe_name)
        
        # 食材も英語に変換
        ingredient_translations = {
            "ピーマン": "green pepper", "玉ねぎ": "onion", "にんじん": "carrot",
            "じゃがいも": "potato", "鶏肉": "chicken", "豚肉": "pork",
            "牛肉": "beef", "卵": "egg", "お米": "rice", "パスタ": "pasta",
            "きのこ類": "mushrooms", "きのこ": "mushrooms"
        }
        
        english_ingredients = []
        for ingredient in ingredients:
            english_ingredient = ingredient_translations.get(ingredient, ingredient)
            english_ingredients.append(english_ingredient)

        # 改良されたプロンプト（英語）
        prompt = f"A delicious, appetizing photograph of {english_recipe}, Japanese home cooking, beautifully plated with {', '.join(english_ingredients)}, professional food photography, natural lighting, high quality, detailed, realistic"
        print(f"Using English prompt: {prompt}")
        
        # 新しいInference Providers APIを試行
        try:
            print("Trying new Inference Providers API...")
            
            # 新しいInference Providersのエンドポイント
            headers = {
                'Authorization': f'Bearer {hf_api_key}',
                'Content-Type': 'application/json'
            }
            
            # 複数のプロバイダーとモデルを試行
            provider_configs = [
                {
                    'url': 'https://router.huggingface.co/fal-ai/image/generation',
                    'provider': 'fal-ai',
                    'model': 'fal-ai/flux-lora'
                },
                {
                    'url': 'https://router.huggingface.co/replicate/image/generation', 
                    'provider': 'replicate',
                    'model': 'stability-ai/stable-diffusion'
                }
            ]
            
            for config in provider_configs:
                try:
                    print(f"Trying provider: {config['provider']}")
                    
                    data = {
                        "inputs": prompt,
                        "model": config['model'],
                        "parameters": {
                            "width": 512,
                            "height": 512,
                            "guidance_scale": 7.5,
                            "num_inference_steps": 20
                        }
                    }
                    
                    response = requests.post(
                        config['url'],
                        headers=headers,
                        json=data,
                        timeout=120
                    )
                    
                    print(f"Provider {config['provider']} response: {response.status_code}")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'application/json' not in content_type and len(response.content) > 1000:
                            image_data = base64.b64encode(response.content).decode('utf-8')
                            print(f"SUCCESS: Generated image with {config['provider']}")
                            return f"data:image/png;base64,{image_data}"
                        else:
                            print(f"Provider {config['provider']} returned JSON or small response")
                            try:
                                json_response = response.json()
                                print(f"JSON response: {json_response}")
                            except:
                                pass
                    else:
                        print(f"Provider {config['provider']} failed with status {response.status_code}")
                        
                except Exception as provider_error:
                    print(f"Provider {config['provider']} error: {str(provider_error)}")
                    continue
                    
        except Exception as providers_error:
            print(f"Inference Providers error: {str(providers_error)}")
        
        # フォールバック：従来のAPIを一度だけ試行
        try:
            print("Trying fallback: traditional API...")
            
            headers = {'Authorization': f'Bearer {hf_api_key}'}
            data = {"inputs": prompt}
            
            # 最も基本的なモデルを1つだけ試行
            response = requests.post(
                'https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5',
                headers=headers, 
                json=data, 
                timeout=60
            )
            
            print(f"Fallback response: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' not in content_type and len(response.content) > 1000:
                    image_data = base64.b64encode(response.content).decode('utf-8')
                    print("SUCCESS: Generated image with fallback API")
                    return f"data:image/png;base64,{image_data}"
                    
        except Exception as fallback_error:
            print(f"Fallback API error: {str(fallback_error)}")
        
        print("All AI image generation methods failed")
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

# 改良されたプレースホルダー画像システム
@app.route('/api/generate-image', methods=['POST'])
def generate_recipe_image():
    try:
        print("=== Smart Placeholder Image generation ===")
        data = request.json
        print(f"Request data: {data}")
        
        recipe_name = data.get('recipe_name')
        ingredients = data.get('ingredients', [])

        print(f"Recipe name: {recipe_name}")
        print(f"Ingredients: {ingredients}")

        if not recipe_name:
            print("ERROR: No recipe name provided")
            return jsonify({'error': 'レシピ名が必要です'}), 400

        # 料理の種類に基づいた高品質なプレースホルダー画像を選択
        food_categories = {
            'rice_dishes': {
                'keywords': ['ご飯', 'おにぎり', 'むすび', '丼', 'チャーハン', '炒飯', '茶漬け', 'おこげ', 'rice'],
                'images': [
                    "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=512&h=512&fit=crop&auto=format&q=80"
                ]
            },
            'noodles': {
                'keywords': ['パスタ', 'うどん', 'そば', '焼きそば', 'ラーメン', 'pasta', 'noodles'],
                'images': [
                    "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1563379091339-03246963d51a?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1555126634-323283e090fa?w=512&h=512&fit=crop&auto=format&q=80"
                ]
            },
            'vegetables': {
                'keywords': ['ピーマン', '野菜', 'サラダ', '炒め', 'vegetables', 'salad'],
                'images': [
                    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1529059997568-3d847b1154f0?w=512&h=512&fit=crop&auto=format&q=80"
                ]
            },
            'meat_dishes': {
                'keywords': ['鶏肉', '豚肉', '牛肉', '肉', '唐揚げ', '焼き', 'chicken', 'pork', 'beef'],
                'images': [
                    "https://images.unsplash.com/photo-1532636875304-0c89119d9b4d?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1544025162-d76694265947?w=512&h=512&fit=crop&auto=format&q=80"
                ]
            },
            'seafood': {
                'keywords': ['魚', '鮭', 'まぐろ', 'えび', '海鮮', 'fish', 'salmon', 'seafood'],
                'images': [
                    "https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1559847844-d05fcb51d842?w=512&h=512&fit=crop&auto=format&q=80"
                ]
            },
            'soups': {
                'keywords': ['スープ', '汁', '味噌汁', 'soup', 'broth'],
                'images': [
                    "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=512&h=512&fit=crop&auto=format&q=80"
                ]
            },
            'default': {
                'keywords': [],
                'images': [
                    "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=512&h=512&fit=crop&auto=format&q=80",
                    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=512&h=512&fit=crop&auto=format&q=80"
                ]
            }
        }
        
        # 料理名から最適なカテゴリを自動判定
        recipe_lower = recipe_name.lower()
        selected_category = 'default'
        
        for category, data in food_categories.items():
            if category == 'default':
                continue
            if any(keyword in recipe_lower for keyword in data['keywords']):
                selected_category = category
                break
        
        # 食材からも判定を補強
        if selected_category == 'default':
            for ingredient in ingredients:
                ingredient_lower = ingredient.lower()
                for category, data in food_categories.items():
                    if category == 'default':
                        continue
                    if any(keyword in ingredient_lower for keyword in data['keywords']):
                        selected_category = category
                        break
                if selected_category != 'default':
                    break
        
        import random
        selected_images = food_categories[selected_category]['images']
        image_url = random.choice(selected_images)
        
        print(f"Selected category: {selected_category}")
        print(f"Using high-quality placeholder image: {image_url}")
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'recipe_name': recipe_name,
            'timestamp': datetime.now().isoformat(),
            'type': 'Smart Placeholder',
            'category': selected_category,
            'note': f'料理カテゴリ「{selected_category}」に基づいた高品質画像を表示中'
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