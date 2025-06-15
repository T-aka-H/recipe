from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import random

# Flaskアプリケーションを作成（staticフォルダを指定）
app = Flask(__name__, static_folder='.', static_url_path='/static')

# ルートディレクトリの静的ファイル配信用
@app.route('/icon-256x256.png')
def serve_icon():
    # Flaskアプリのルートディレクトリを取得
    app_root = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_root, 'icon-256x256.png')
    
    print(f"アイコンルートが呼ばれました！")
    print(f"app.pyの場所: {__file__}")
    print(f"アプリルート: {app_root}")
    print(f"現在のディレクトリ: {os.getcwd()}")
    print(f"アイコンパス: {icon_path}")
    print(f"ファイル一覧: {os.listdir(app_root)}")
    
    try:
        if os.path.exists(icon_path):
            print("アイコンファイルが見つかりました")
            return send_from_directory(app_root, 'icon-256x256.png', mimetype='image/png')
        else:
            print("アイコンファイルが見つかりません")
            return "Icon not found", 404
    except Exception as e:
        print(f"アイコン配信エラー: {e}")
        return f"Icon error: {str(e)}", 500

@app.route('/manifest.json')
def serve_manifest():
    # Flaskアプリのルートディレクトリを取得
    app_root = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(app_root, 'manifest.json')
    
    print("Manifestルートが呼ばれました")
    print(f"Manifestパス: {manifest_path}")
    
    try:
        if os.path.exists(manifest_path):
            print("Manifestファイルが見つかりました")
            return send_from_directory(app_root, 'manifest.json', mimetype='application/json')
        else:
            print("Manifestファイルが見つかりません")
            return "Manifest not found", 404
    except Exception as e:
        print(f"Manifest配信エラー: {e}")
        return f"Manifest error: {str(e)}", 500

# Apple Touch Icon用ルート
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
        print(f"Apple Touch Icon配信エラー: {e}")
        return f"Apple icon error: {str(e)}", 500

# favicon.ico用ルート
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

# デバッグ用エンドポイント
@app.route('/debug-files')
def debug_files():
    try:
        app_root = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.getcwd()
        
        # 複数の場所をチェック
        locations_to_check = [
            ('app.pyと同じディレクトリ', app_root),
            ('現在の作業ディレクトリ', current_dir),
        ]
        
        result = f"""
        <h2>デバッグ情報 - Render環境</h2>
        <p><strong>app.pyの場所:</strong> {__file__}</p>
        <p><strong>アプリルートディレクトリ:</strong> {app_root}</p>
        <p><strong>現在の作業ディレクトリ:</strong> {current_dir}</p>
        <hr>
        """
        
        for location_name, path in locations_to_check:
            try:
                files_in_dir = os.listdir(path)
                icon_path = os.path.join(path, 'icon-256x256.png')
                manifest_path = os.path.join(path, 'manifest.json')
                
                icon_exists = os.path.exists(icon_path)
                manifest_exists = os.path.exists(manifest_path)
                
                icon_size = os.path.getsize(icon_path) if icon_exists else 0
                manifest_size = os.path.getsize(manifest_path) if manifest_exists else 0
                
                result += f"""
                <h3>{location_name}: {path}</h3>
                <p><strong>icon-256x256.png存在:</strong> {icon_exists} ({icon_size} bytes)</p>
                <p><strong>manifest.json存在:</strong> {manifest_exists} ({manifest_size} bytes)</p>
                <p><strong>ファイル一覧:</strong></p>
                <ul>
                {"".join([f"<li>{f}</li>" for f in files_in_dir])}
                </ul>
                <hr>
                """
            except Exception as e:
                result += f"<p><strong>{location_name}でエラー:</strong> {str(e)}</p><hr>"
        
        result += """
        <p><a href="/icon-256x256.png">アイコンに直接アクセス</a></p>
        <p><a href="/manifest.json">Manifestに直接アクセス</a></p>
        """
        
        return result
        
    except Exception as e:
        return f"デバッグエラー: {str(e)}"

@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    try:
        data = request.get_json()
        mood = data.get('mood')
        ingredients = data.get('ingredients', [])
        
        # 食材名の日本語マッピング
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
        
        # サンプルレシピ生成
        sample_recipes = f"""【気分・好み】: {mood_name}
【使用可能な食材】: {', '.join(selected_ingredient_names)}

以下、5つのおすすめレシピをご提案します：

1. **{selected_ingredient_names[0] if selected_ingredient_names else '野菜'}と{selected_ingredient_names[1] if len(selected_ingredient_names) > 1 else '玉ねぎ'}の炒め物**
   - 調理時間: 15分
   - 難易度: ★☆☆（初心者向け）
   - 材料: {', '.join(selected_ingredient_names[:3])}、醤油、塩、胡椒
   - 作り方: 
     1. 食材を適当な大きさに切る
     2. フライパンで炒める
     3. 調味料で味付けして完成
   - ポイント: 強火で手早く炒めると食材の食感が残って美味しい

2. **簡単{selected_ingredient_names[0] if selected_ingredient_names else '野菜'}料理**
   - 調理時間: 20分
   - 難易度: ★★☆（中級者向け）
   - 材料: {', '.join(selected_ingredient_names[:4])}、だし、みりん
   - 作り方: 
     1. 下準備をしっかりと行う
     2. 順番に加熱していく
     3. 調味料を加えて煮込む
     4. 味を調えて完成
   - ポイント: {mood_name}な気分にぴったりの優しい味付け

3. **{selected_ingredient_names[1] if len(selected_ingredient_names) > 1 else '野菜'}たっぷりヘルシー料理**
   - 調理時間: 25分
   - 難易度: ★★☆（中級者向け）
   - 材料: {', '.join(selected_ingredient_names)}、オリーブオイル、塩
   - 作り方: 
     1. 野菜類は食べやすい大きさに切る
     2. オリーブオイルで炒める
     3. 蒸し焼きにしてじっくり火を通す
     4. 塩で味を調える
   - ポイント: 野菜の甘みを活かした健康的な一品

4. **和風{selected_ingredient_names[0] if selected_ingredient_names else '野菜'}丼**
   - 調理時間: 30分
   - 難易度: ★★★（上級者向け）
   - 材料: {', '.join(selected_ingredient_names[:3])}、ご飯、卵、醤油、みりん、砂糖
   - 作り方: 
     1. 具材を下ごしらえする
     2. 調味料を合わせて煮汁を作る
     3. 具材を煮込む
     4. 卵でとじてご飯にのせる
   - ポイント: 卵は半熟状態で火を止めると美味しい

5. **創作{selected_ingredient_names[2] if len(selected_ingredient_names) > 2 else 'ミックス'}料理**
   - 調理時間: 35分
   - 難易度: ★★☆（中級者向け）
   - 材料: {', '.join(selected_ingredient_names)}、お好みの調味料
   - 作り方: 
     1. すべての食材を準備する
     2. 食材の特性に合わせて順番に調理
     3. 最後に全体を合わせる
     4. お好みで調味料を追加
   - ポイント: {mood_name}な気分に合わせてアレンジ自在

どのレシピも{mood_name}な今日にぴったりです！お気に入りのレシピで美味しい料理を作ってくださいね🍴"""
        
        return jsonify({
            'success': True,
            'recipes': sample_recipes
        })
        
    except Exception as e:
        print(f"レシピ生成エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        
        # ランダムな画像を選択
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
    app.run(debug=True)