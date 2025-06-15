from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import random
import itertools
import json
import time
from datetime import datetime, timedelta
import google.generativeai as genai

# Flaskアプリケーションを作成
app = Flask(__name__, static_folder='.', static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Gemini API設定
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("警告: GEMINI_API_KEYが設定されていません。AI機能は無効になります。")
    model = None

# 設定値
AI_MODE_ENABLED = os.environ.get('AI_MODE_ENABLED', 'true').lower() == 'true'
DAILY_AI_LIMIT = int(os.environ.get('DAILY_AI_LIMIT', '50'))  # 1日あたりのAI使用回数制限
AI_GENERATION_RATE = float(os.environ.get('AI_GENERATION_RATE', '0.7'))  # AI生成の確率（70%）

# 使用回数管理用の簡易ストレージ（本番環境ではRedisやDBを使用）
usage_tracker = {}

def get_daily_usage_key():
    """今日の日付ベースのキーを生成"""
    return datetime.now().strftime('%Y-%m-%d')

def increment_ai_usage():
    """AI使用回数をインクリメント"""
    key = get_daily_usage_key()
    if key not in usage_tracker:
        usage_tracker[key] = 0
    usage_tracker[key] += 1

def can_use_ai():
    """AI使用可能かチェック"""
    if not model or not AI_MODE_ENABLED:
        return False
    
    key = get_daily_usage_key()
    current_usage = usage_tracker.get(key, 0)
    return current_usage < DAILY_AI_LIMIT

def should_use_ai():
    """AI生成すべきかランダム判定（A/Bテスト用）"""
    return random.random() < AI_GENERATION_RATE

# 既存の静的ファイル配信ルート
@app.route('/icon-256x256.png')
def serve_icon():
    app_root = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_root, 'icon-256x256.png')
    
    try:
        if os.path.exists(icon_path):
            return send_from_directory(app_root, 'icon-256x256.png', mimetype='image/png')
        else:
            return "Icon not found", 404
    except Exception as e:
        return f"Icon error: {str(e)}", 500

@app.route('/manifest.json')
def serve_manifest():
    app_root = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(app_root, 'manifest.json')
    
    try:
        if os.path.exists(manifest_path):
            return send_from_directory(app_root, 'manifest.json', mimetype='application/json')
        else:
            return "Manifest not found", 404
    except Exception as e:
        return f"Manifest error: {str(e)}", 500

@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-120x120.png')
@app.route('/apple-touch-icon-120x120-precomposed.png')
@app.route('/apple-touch-icon-180x180.png')
def serve_apple_icon():
    app_root = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_root, 'icon-256x256.png')
    
    try:
        if os.path.exists(icon_path):
            return send_from_directory(app_root, 'icon-256x256.png', mimetype='image/png')
        else:
            return "Apple icon not found", 404
    except Exception as e:
        return f"Apple icon error: {str(e)}", 500

@app.route('/favicon.ico')
def serve_favicon():
    app_root = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_root, 'icon-256x256.png')
    
    try:
        if os.path.exists(icon_path):
            return send_from_directory(app_root, 'icon-256x256.png', mimetype='image/png')
        else:
            return "Favicon not found", 404
    except Exception as e:
        return f"Favicon error: {str(e)}", 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug-files')
def debug_files():
    try:
        app_root = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.getcwd()
        
        result = f"""
        <h2>デバッグ情報</h2>
        <p><strong>AI機能:</strong> {'有効' if model else '無効'}</p>
        <p><strong>今日のAI使用回数:</strong> {usage_tracker.get(get_daily_usage_key(), 0)} / {DAILY_AI_LIMIT}</p>
        <p><strong>AI生成確率:</strong> {AI_GENERATION_RATE * 100}%</p>
        <hr>
        <p><strong>app.pyの場所:</strong> {__file__}</p>
        <p><strong>アプリルートディレクトリ:</strong> {app_root}</p>
        <p><strong>現在の作業ディレクトリ:</strong> {current_dir}</p>
        """
        
        return result
        
    except Exception as e:
        return f"デバッグエラー: {str(e)}"

# AI生成レシピ機能
def generate_ai_recipe(mood, ingredients, context="", user_preferences=""):
    """Gemini 1.5 Flashを使用してレシピを生成"""
    try:
        # 食材名の日本語変換
        ingredient_names = {
            'rice': 'お米', 'pasta': 'パスタ', 'bread': 'パン', 'udon': 'うどん', 'soba': 'そば',
            'chicken': '鶏肉', 'pork': '豚肉', 'beef': '牛肉', 'ground_meat': 'ひき肉',
            'salmon': '鮭', 'tuna': 'まぐろ', 'shrimp': 'えび',
            'egg': '卵', 'milk': '牛乳', 'cheese': 'チーズ', 'tofu': '豆腐', 'natto': '納豆',
            'onion': '玉ねぎ', 'carrot': 'にんじん', 'potato': 'じゃがいも', 'cabbage': 'キャベツ',
            'tomato': 'トマト', 'cucumber': 'きゅうり', 'lettuce': 'レタス', 'spinach': 'ほうれん草',
            'mushroom': 'きのこ類', 'bell_pepper': 'ピーマン', 'banana': 'バナナ', 'apple': 'りんご', 'lemon': 'レモン'
        }
        
        mood_descriptions = {
            'happy': '元気いっぱいで楽しい気分',
            'tired': '疲れていて簡単で栄養のあるものが欲しい',
            'healthy': 'ヘルシーで体に良いものを食べたい',
            'comfort': '懐かしくて心温まる家庭的な料理が欲しい',
            'adventure': '新しい味や珍しい料理に挑戦したい',
            'spicy': '辛くて刺激的な料理が食べたい'
        }
        
        japanese_ingredients = [ingredient_names.get(ing, ing) for ing in ingredients]
        mood_desc = mood_descriptions.get(mood, mood)
        
        prompt = f"""あなたは料理研究家で、親しみやすく実用的なレシピを提案する専門家です。

**今回の状況:**
- 気分: {mood_desc}
- 使用できる食材: {', '.join(japanese_ingredients)}
- 追加の要望: {context}
- 好み: {user_preferences}

**お願い:**
上記の状況を考慮して、実際に作れる美味しいレシピを1つ提案してください。

**回答形式（必ずこの形式で回答してください）:**

## レシピ名
（魅力的で分かりやすい名前）

## 調理情報
- ⏰ 調理時間: XX分
- 📊 難易度: ★☆☆ または ★★☆ または ★★★
- 🍽️ 人数: X人分

## 材料
（具体的な分量も含めて）
- 主な食材（3-5個）
- 調味料・その他（3-5個）

## 作り方
1. 【下準備】具体的な準備内容
2. 【工程1】詳細な手順
3. 【工程2】詳細な手順
4. 【工程3】詳細な手順
5. 【完成】仕上げの手順

## コツ・ポイント
（失敗しないための具体的なアドバイス）

## なぜこのレシピなのか
（今の気分や状況にぴったりな理由）

**重要な注意事項:**
- 実際に作れるレシピにしてください
- 分量は具体的に書いてください
- 調理時間は現実的にしてください
- 使用できる食材を中心に構成してください（すべて使う必要はありません）"""

        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"AI生成エラー: {e}")
        return None

# 従来のルールベースレシピ生成（フォールバック用）
def generate_rule_based_recipe(mood, ingredients):
    """従来のルールベースでレシピ生成（フォールバック用）"""
    ingredient_names = {
        'rice': 'お米', 'pasta': 'パスタ', 'bread': 'パン', 'udon': 'うどん', 'soba': 'そば',
        'chicken': '鶏肉', 'pork': '豚肉', 'beef': '牛肉', 'ground_meat': 'ひき肉',
        'salmon': '鮭', 'tuna': 'まぐろ', 'shrimp': 'えび',
        'egg': '卵', 'milk': '牛乳', 'cheese': 'チーズ', 'tofu': '豆腐', 'natto': '納豆',
        'onion': '玉ねぎ', 'carrot': 'にんじん', 'potato': 'じゃがいも', 'cabbage': 'キャベツ',
        'tomato': 'トマト', 'cucumber': 'きゅうり', 'lettuce': 'レタス', 'spinach': 'ほうれん草',
        'mushroom': 'きのこ類', 'bell_pepper': 'ピーマン', 'banana': 'バナナ', 'apple': 'りんご', 'lemon': 'レモン'
    }
    
    mood_recipes = {
        'happy': {
            'name': f'元気いっぱい{ingredient_names.get(ingredients[0] if ingredients else "野菜", "野菜")}炒め',
            'time': '15分',
            'difficulty': '★★☆',
            'ingredients': [ingredient_names.get(ing, ing) for ing in ingredients[:3]],
            'seasonings': ['醤油', 'みりん', 'ごま油', '塩'],
            'steps': [
                '材料を食べやすい大きさに切る',
                'フライパンを熱して炒める',
                '調味料で味付けして完成'
            ],
            'tips': '強火で手早く炒めると美味しくなります'
        },
        'tired': {
            'name': f'疲労回復{ingredient_names.get(ingredients[0] if ingredients else "野菜", "野菜")}スープ',
            'time': '20分',
            'difficulty': '★☆☆',
            'ingredients': [ingredient_names.get(ing, ing) for ing in ingredients[:3]],
            'seasonings': ['コンソメ', '塩', 'こしょう'],
            'steps': [
                '材料を切る',
                '鍋で煮込む',
                '調味料で味を調える'
            ],
            'tips': '疲れた体に優しい味です'
        }
    }
    
    recipe = mood_recipes.get(mood, mood_recipes['happy'])
    
    return f"""## {recipe['name']}

## 調理情報
- ⏰ 調理時間: {recipe['time']}
- 📊 難易度: {recipe['difficulty']}
- 🍽️ 人数: 2人分

## 材料
- {', '.join(recipe['ingredients'])}
- {', '.join(recipe['seasonings'])}

## 作り方
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(recipe['steps'])])}

## コツ・ポイント
{recipe['tips']}

## なぜこのレシピなのか
今の気分にぴったりの基本的なレシピです。

---
*このレシピは従来システムで生成されました*"""

@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    try:
        data = request.get_json()
        mood = data.get('mood', 'happy')
        ingredients = data.get('ingredients', [])
        context = data.get('context', '')  # 追加の要望
        force_ai = data.get('force_ai', False)  # AI強制使用フラグ
        
        # 食材名変換
        ingredient_names = {
            'rice': 'お米', 'pasta': 'パスタ', 'bread': 'パン', 'udon': 'うどん', 'soba': 'そば',
            'chicken': '鶏肉', 'pork': '豚肉', 'beef': '牛肉', 'ground_meat': 'ひき肉',
            'salmon': '鮭', 'tuna': 'まぐろ', 'shrimp': 'えび',
            'egg': '卵', 'milk': '牛乳', 'cheese': 'チーズ', 'tofu': '豆腐', 'natto': '納豆',
            'onion': '玉ねぎ', 'carrot': 'にんじん', 'potato': 'じゃがいも', 'cabbage': 'キャベツ',
            'tomato': 'トマト', 'cucumber': 'きゅうり', 'lettuce': 'レタス', 'spinach': 'ほうれん草',
            'mushroom': 'きのこ類', 'bell_pepper': 'ピーマン', 'banana': 'バナナ', 'apple': 'りんご', 'lemon': 'レモン'
        }
        
        mood_names = {
            'happy': '元気いっぱい',
            'tired': '疲れ気味',
            'healthy': 'ヘルシー志向',
            'comfort': '家庭的な気分',
            'adventure': '冒険したい',
            'spicy': 'スパイシー'
        }
        
        selected_ingredient_names = [ingredient_names.get(ing, ing) for ing in ingredients]
        mood_name = mood_names.get(mood, mood)
        
        # ユーザーの過去の好みを取得（セッションから）
        user_preferences = session.get('user_preferences', '')
        
        # AI生成 vs ルールベース判定
        use_ai = False
        generation_method = "rule_based"
        
        if force_ai or (can_use_ai() and should_use_ai()):
            # AI生成を試行
            print("AI生成を試行中...")
            ai_recipe = generate_ai_recipe(mood, ingredients, context, user_preferences)
            
            if ai_recipe:
                increment_ai_usage()
                use_ai = True
                generation_method = "ai_generated"
                
                # セッションに使用状況を記録
                if 'recipe_history' not in session:
                    session['recipe_history'] = []
                
                session['recipe_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'mood': mood,
                    'ingredients': ingredients,
                    'method': 'ai',
                    'success': True
                })
                
                recipes_text = f"""【今日の気分】: {mood_name}
【使用可能な食材】: {', '.join(selected_ingredient_names)}
【生成方法】: 🤖 AI Chef（Gemini 1.5 Flash）

{ai_recipe}

---
💡 **AI Chefより**: このレシピはあなたの気分と食材を考慮して特別に作成しました！
🔄 **より良いレシピを**: 「もう少し簡単に」「辛くして」などの要望があれば、再度お試しください。
📝 **フィードバック**: 作ってみた感想を教えていただけると、次回より良い提案ができます。"""
                
                return jsonify({
                    'success': True,
                    'recipes': recipes_text,
                    'generation_method': generation_method,
                    'ai_usage_remaining': DAILY_AI_LIMIT - usage_tracker.get(get_daily_usage_key(), 0)
                })
        
        # フォールバック: ルールベースレシピ生成
        print("ルールベース生成にフォールバック")
        rule_recipe = generate_rule_based_recipe(mood, ingredients)
        
        # セッションに記録
        if 'recipe_history' not in session:
            session['recipe_history'] = []
        
        session['recipe_history'].append({
            'timestamp': datetime.now().isoformat(),
            'mood': mood,
            'ingredients': ingredients,
            'method': 'rule_based',
            'success': True
        })
        
        recipes_text = f"""【今日の気分】: {mood_name}
【使用可能な食材】: {', '.join(selected_ingredient_names)}
【生成方法】: 📋 クラシックレシピ

{rule_recipe}

---
🤖 **AI Chefを試してみませんか？**: より創造的でパーソナライズされたレシピをお求めなら、「AI Chef」ボタンをお試しください！
⚡ **今日のAI使用可能回数**: あと{DAILY_AI_LIMIT - usage_tracker.get(get_daily_usage_key(), 0)}回"""
        
        return jsonify({
            'success': True,
            'recipes': recipes_text,
            'generation_method': generation_method,
            'ai_usage_remaining': DAILY_AI_LIMIT - usage_tracker.get(get_daily_usage_key(), 0)
        })
        
    except Exception as e:
        print(f"レシピ生成エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'generation_method': 'error'
        }), 500

# AI Chef専用エンドポイント
@app.route('/api/ai-chef', methods=['POST'])
def ai_chef_chat():
    """AI Chefとの対話専用エンドポイント"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        mood = data.get('mood', 'happy')
        ingredients = data.get('ingredients', [])
        
        if not can_use_ai():
            return jsonify({
                'success': False,
                'error': f'今日のAI使用回数上限（{DAILY_AI_LIMIT}回）に達しました。明日再度お試しください。',
                'ai_usage_remaining': 0
            }), 429
        
        # 会話履歴を考慮したプロンプト
        conversation_history = session.get('ai_conversation', [])
        
        # 食材の日本語変換
        ingredient_names = {
            'rice': 'お米', 'pasta': 'パスタ', 'bread': 'パン', 'udon': 'うどん', 'soba': 'そば',
            'chicken': '鶏肉', 'pork': '豚肉', 'beef': '牛肉', 'ground_meat': 'ひき肉',
            'salmon': '鮭', 'tuna': 'まぐろ', 'shrimp': 'えび',
            'egg': '卵', 'milk': '牛乳', 'cheese': 'チーズ', 'tofu': '豆腐', 'natto': '納豆',
            'onion': '玉ねぎ', 'carrot': 'にんじん', 'potato': 'じゃがいも', 'cabbage': 'キャベツ',
            'tomato': 'トマト', 'cucumber': 'きゅうり', 'lettuce': 'レタス', 'spinach': 'ほうれん草',
            'mushroom': 'きのこ類', 'bell_pepper': 'ピーマン', 'banana': 'バナナ', 'apple': 'りんご', 'lemon': 'レモン'
        }
        
        japanese_ingredients = [ingredient_names.get(ing, ing) for ing in ingredients]
        
        context = f"""あなたは親しみやすいAI料理シェフです。ユーザーとフレンドリーに会話しながら、実用的な料理アドバイスを提供してください。

現在の状況:
- ユーザーの気分: {mood}
- 利用可能な食材: {', '.join(japanese_ingredients)}
- ユーザーからのメッセージ: "{user_message}"

過去の会話履歴:
{chr(10).join([f'ユーザー: {h["user"]}' + chr(10) + f'AI Chef: {h["ai"]}' for h in conversation_history[-3:]])}

以下の点に注意して回答してください:
1. フレンドリーで親しみやすい口調
2. 実際に作れる具体的なアドバイス
3. 必要に応じてレシピや調理のコツを提供
4. 食材の代替案や応用も提案
5. 簡潔で分かりやすい説明"""

        response = model.generate_content(context)
        ai_response = response.text.strip()
        
        # 会話履歴を更新
        if 'ai_conversation' not in session:
            session['ai_conversation'] = []
        
        session['ai_conversation'].append({
            'user': user_message,
            'ai': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 古い会話履歴を削除（最新10件のみ保持）
        if len(session['ai_conversation']) > 10:
            session['ai_conversation'] = session['ai_conversation'][-10:]
        
        increment_ai_usage()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'ai_usage_remaining': DAILY_AI_LIMIT - usage_tracker.get(get_daily_usage_key(), 0)
        })
        
    except Exception as e:
        print(f"AI Chat エラー: {e}")
        return jsonify({
            'success': False,
            'error': f'AI Chefが一時的に利用できません: {str(e)}'
        }), 500

# フィードバック機能
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """ユーザーフィードバックを受信"""
    try:
        data = request.get_json()
        feedback_type = data.get('type')  # 'like', 'dislike', 'suggestion'
        feedback_text = data.get('text', '')
        recipe_data = data.get('recipe_data', {})
        
        # セッションにフィードバックを保存（本番環境ではDBに保存）
        if 'feedback_history' not in session:
            session['feedback_history'] = []
        
        session['feedback_history'].append({
            'type': feedback_type,
            'text': feedback_text,
            'recipe_data': recipe_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # ユーザーの好みを学習（簡易版）
        if feedback_type == 'like':
            preferences = session.get('user_preferences', '')
            if recipe_data.get('generation_method') == 'ai_generated':
                preferences += f" 好み: {recipe_data.get('mood', '')}の時の料理,"
            session['user_preferences'] = preferences[-500:]  # 最新500文字のみ保持
        
        return jsonify({
            'success': True,
            'message': 'フィードバックありがとうございます！次回の提案に活用させていただきます。'
        })
        
    except Exception as e:
        print(f"フィードバックエラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 統計情報エンドポイント
@app.route('/api/stats')
def get_stats():
    """利用統計を返す"""
    try:
        today_key = get_daily_usage_key()
        
        return jsonify({
            'ai_enabled': model is not None,
            'daily_limit': DAILY_AI_LIMIT,
            'today_usage': usage_tracker.get(today_key, 0),
            'remaining_usage': DAILY_AI_LIMIT - usage_tracker.get(today_key, 0),
            'ai_generation_rate': AI_GENERATION_RATE,
            'user_session_recipes': len(session.get('recipe_history', [])),
            'user_feedback_count': len(session.get('feedback_history', []))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 画像生成API（既存）
@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        recipe_name = data.get('recipe_name')
        ingredients = data.get('ingredients', [])
        
        # サンプル画像URLs
        sample_images = [
            'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=512&h=512&fit=crop&auto=format&q=80',
            'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=512&h=512&fit=crop&auto=format&q=80',
            'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=512&h=512&fit=crop&auto=format&q=80',
            'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=512&h=512&fit=crop&auto=format&q=80',
            'https://images.unsplash.com/photo-1516684810915-8c1de8b4bb61?w=512&h=512&fit=crop&auto=format&q=80'
        ]
        
        selected_image = random.choice(sample_images)
        
        return jsonify({
            'success': True,
            'image_url': selected_image
        })
        
    except Exception as e:
        print(f"画像生成エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # 起動時の情報表示
    print("🍳 AI Recipe App 起動中...")
    print(f"🤖 AI機能: {'有効' if model else '無効'}")
    print(f"📊 1日のAI使用上限: {DAILY_AI_LIMIT}回")
    print(f"🎲 AI生成確率: {AI_GENERATION_RATE * 100}%")
    print(f"🔑 API Key設定: {'✅' if GEMINI_API_KEY else '❌'}")
    
    app.run(debug=True)