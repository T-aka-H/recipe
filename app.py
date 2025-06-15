from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import random
import itertools

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
        
        # 調理方法のパターン
        cooking_methods = {
            'stir_fry': '炒め物',
            'soup': 'スープ',
            'rice_dish': 'ご飯もの',
            'noodle': '麺類',
            'grilled': '焼き物',
            'steamed': '蒸し物',
            'boiled': '煮物',
            'salad': 'サラダ',
            'sandwich': 'サンドイッチ',
            'pasta': 'パスタ',
            'curry': 'カレー',
            'omelette': 'オムレツ'
        }
        
        # 気分別の調理方法の重み付け
        mood_cooking_weights = {
            'happy': {'stir_fry': 3, 'rice_dish': 3, 'pasta': 2, 'omelette': 2, 'grilled': 1},
            'tired': {'soup': 4, 'rice_dish': 3, 'noodle': 3, 'omelette': 2, 'boiled': 1},
            'healthy': {'salad': 4, 'steamed': 3, 'grilled': 3, 'soup': 2, 'stir_fry': 1},
            'comfort': {'boiled': 4, 'soup': 3, 'rice_dish': 3, 'curry': 2, 'noodle': 1},
            'adventure': {'curry': 3, 'pasta': 3, 'stir_fry': 2, 'grilled': 2, 'sandwich': 1},
            'spicy': {'stir_fry': 4, 'curry': 3, 'noodle': 2, 'soup': 2, 'rice_dish': 1}
        }
        
        # 食材の組み合わせパターン
        def get_ingredient_combinations(ingredients_list):
            if not ingredients_list:
                return [['egg', 'onion']]  # デフォルト
            
            combinations = []
            # 2-4個の食材を使った組み合わせを生成
            for size in [2, 3, 4]:
                if len(ingredients_list) >= size:
                    for combo in itertools.combinations(ingredients_list, min(size, len(ingredients_list))):
                        combinations.append(list(combo))
            
            # 単一食材も含む
            for ingredient in ingredients_list:
                combinations.append([ingredient])
            
            return combinations[:15]  # 最大15個の組み合わせ
        
        # 重み付きランダム選択
        def weighted_random_choice(weights_dict):
            choices = list(weights_dict.keys())
            weights = list(weights_dict.values())
            return random.choices(choices, weights=weights, k=1)[0]
        
        # 動的レシピ生成
        def generate_dynamic_recipe(mood, ingredient_combo):
            # 調理方法を重み付きで選択
            cooking_method = weighted_random_choice(mood_cooking_weights.get(mood, {'stir_fry': 1}))
            
            # 主要食材を決定
            proteins = [ing for ing in ingredient_combo if ing in ['chicken', 'pork', 'beef', 'ground_meat', 'salmon', 'tuna', 'shrimp', 'egg', 'tofu']]
            carbs = [ing for ing in ingredient_combo if ing in ['rice', 'pasta', 'bread', 'udon', 'soba', 'potato']]
            vegetables = [ing for ing in ingredient_combo if ing in ['onion', 'carrot', 'cabbage', 'tomato', 'cucumber', 'lettuce', 'spinach', 'mushroom', 'bell_pepper']]
            
            main_protein = proteins[0] if proteins else None
            main_carb = carbs[0] if carbs else None
            main_vegetables = vegetables[:3]
            
            # 気分に応じた味付けスタイル
            seasoning_styles = {
                'happy': ['甘辛', 'カラフル', '華やか', '楽しい', 'ポップな'],
                'tired': ['優しい', 'あっさり', 'ほっこり', '疲労回復', 'やわらか'],
                'healthy': ['さっぱり', 'ヘルシー', '素材本来', '栄養満点', '体に優しい'],
                'comfort': ['懐かしい', '家庭的', 'ほっとする', '温かい', 'おふくろの味'],
                'adventure': ['エキゾチック', 'スパイシー', '本格', '異国風', '創作'],
                'spicy': ['激辛', 'ピリ辛', 'スパイシー', '刺激的', '燃える']
            }
            
            style = random.choice(seasoning_styles.get(mood, ['基本']))
            
            # レシピ名の生成
            recipe_name = generate_recipe_name(cooking_method, main_protein, main_vegetables, style)
            
            # 調理時間と難易度の決定
            time_difficulty = get_time_and_difficulty(cooking_method, len(ingredient_combo))
            
            # 材料リストの生成
            main_ingredients = []
            if main_protein:
                main_ingredients.append(ingredient_names[main_protein])
            if main_carb:
                main_ingredients.append(ingredient_names[main_carb])
            for veg in main_vegetables:
                main_ingredients.append(ingredient_names[veg])
            
            # 調味料の選択
            seasonings = get_seasonings_for_method_and_mood(cooking_method, mood)
            
            # 詳細な手順の生成
            steps = generate_cooking_steps(cooking_method, ingredient_combo, mood)
            
            # コツの生成
            tips = generate_cooking_tips(cooking_method, mood, main_protein)
            
            return {
                'name': recipe_name,
                'time': time_difficulty['time'],
                'difficulty': time_difficulty['difficulty'],
                'main_ingredients': main_ingredients,
                'seasonings': seasonings,
                'detailed_steps': steps,
                'tips': tips,
                'serving': time_difficulty['serving']
            }
        
        def generate_recipe_name(cooking_method, protein, vegetables, style):
            method_names = {
                'stir_fry': '炒め',
                'soup': 'スープ',
                'rice_dish': '丼',
                'noodle': '麺',
                'grilled': '焼き',
                'steamed': '蒸し',
                'boiled': '煮',
                'salad': 'サラダ',
                'sandwich': 'サンド',
                'pasta': 'パスタ',
                'curry': 'カレー',
                'omelette': 'オムレツ'
            }
            
            if protein and vegetables:
                veg_name = ingredient_names[vegetables[0]]
                protein_name = ingredient_names[protein]
                return f'{style}{protein_name}と{veg_name}の{method_names[cooking_method]}'
            elif protein:
                protein_name = ingredient_names[protein]
                return f'{style}{protein_name}{method_names[cooking_method]}'
            elif vegetables:
                veg_name = ingredient_names[vegetables[0]]
                return f'{style}{veg_name}{method_names[cooking_method]}'
            else:
                return f'{style}野菜{method_names[cooking_method]}'
        
        def get_time_and_difficulty(cooking_method, ingredient_count):
            base_times = {
                'stir_fry': 15, 'soup': 20, 'rice_dish': 25, 'noodle': 18,
                'grilled': 20, 'steamed': 25, 'boiled': 35, 'salad': 10,
                'sandwich': 8, 'pasta': 20, 'curry': 40, 'omelette': 12
            }
            
            base_time = base_times.get(cooking_method, 20)
            actual_time = base_time + (ingredient_count * 2)
            
            if actual_time <= 15:
                difficulty = '★☆☆'
                serving = '1-2人分'
            elif actual_time <= 25:
                difficulty = '★★☆'
                serving = '2人分'
            else:
                difficulty = '★★★'
                serving = '2-3人分'
            
            return {
                'time': f'{actual_time}分',
                'difficulty': difficulty,
                'serving': serving
            }
        
        def get_seasonings_for_method_and_mood(cooking_method, mood):
            base_seasonings = {
                'stir_fry': ['醤油', 'ごま油', '塩', 'こしょう'],
                'soup': ['コンソメ', '塩', 'こしょう', 'バター'],
                'rice_dish': ['醤油', 'みりん', 'だし汁'],
                'noodle': ['だし汁', '醤油', 'ごま油'],
                'grilled': ['塩', 'こしょう', 'オリーブオイル'],
                'steamed': ['塩', 'レモン汁', 'ハーブ'],
                'boiled': ['だし汁', '醤油', 'みりん', '砂糖'],
                'salad': ['オリーブオイル', 'レモン汁', '塩'],
                'sandwich': ['マヨネーズ', 'マスタード', '塩'],
                'pasta': ['オリーブオイル', 'にんにく', '塩', 'パルメザンチーズ'],
                'curry': ['カレー粉', 'コンソメ', '塩', 'こしょう'],
                'omelette': ['塩', 'こしょう', 'バター', '牛乳']
            }
            
            mood_additions = {
                'happy': ['はちみつ', 'ケチャップ', 'マヨネーズ'],
                'tired': ['生姜', '昆布だし', '味の素'],
                'healthy': ['レモン汁', 'ハーブソルト', 'オリーブオイル'],
                'comfort': ['味噌', 'みりん', 'バター'],
                'adventure': ['スパイス', 'ハーブ', 'ガーリック'],
                'spicy': ['唐辛子', 'コチュジャン', '一味', 'タバスコ']
            }
            
            seasonings = base_seasonings.get(cooking_method, ['塩', 'こしょう']).copy()
            mood_items = mood_additions.get(mood, [])
            
            if mood_items:
                seasonings.extend(random.sample(mood_items, min(2, len(mood_items))))
            
            return seasonings
        
        def generate_cooking_steps(cooking_method, ingredients, mood):
            # 基本的な調理手順のテンプレート
            step_templates = {
                'stir_fry': [
                    '【下準備】すべての材料を食べやすい大きさに切る',
                    '【加熱】フライパンを中火で熱し、油を入れる',
                    '【炒める】火の通りにくいものから順番に炒める',
                    '【調味】調味料を加えて味を調える',
                    '【仕上げ】強火で30秒炒めて完成'
                ],
                'soup': [
                    '【材料カット】すべての材料を適当な大きさに切る',
                    '【炒める】鍋で材料を軽く炒める',
                    '【水を加える】水とだしを加えて煮立てる',
                    '【煮込む】中火で10-15分煮込む',
                    '【調味】塩こしょうで味を調えて完成'
                ],
                'rice_dish': [
                    '【材料準備】具材を食べやすく切る',
                    '【炒める】フライパンで具材を炒める',
                    '【ご飯投入】温かいご飯を加える',
                    '【調味】調味料で味付けする',
                    '【仕上げ】全体を混ぜ合わせて完成'
                ],
                'noodle': [
                    '【麺を茹でる】表示時間通りに麺を茹でる',
                    '【具材準備】具材を食べやすく切る',
                    '【スープ作り】別の鍋でスープを作る',
                    '【合わせる】茹でた麺にスープと具材をのせる',
                    '【完成】お好みで薬味を加えて完成'
                ],
                'grilled': [
                    '【下味】材料に塩こしょうで下味をつける',
                    '【予熱】グリルパンまたはフライパンを熱する',
                    '【焼く】両面をしっかりと焼く',
                    '【火加減】中火でじっくり火を通す',
                    '【完成】焼き色が付いたら完成'
                ],
                'steamed': [
                    '【材料準備】材料を均一な大きさに切る',
                    '【蒸し器準備】蒸し器に水を入れて沸騰させる',
                    '【蒸す】材料を蒸し器に入れて蒸す',
                    '【確認】竹串を刺して火の通りを確認',
                    '【調味】お好みの調味料をかけて完成'
                ],
                'boiled': [
                    '【材料準備】材料を大きめに切る',
                    '【炒める】鍋で材料を軽く炒める',
                    '【だしを加える】だし汁を加えて煮立てる',
                    '【煮込む】落し蓋をして弱火で煮込む',
                    '【味付け】調味料を加えて味を調える'
                ],
                'salad': [
                    '【野菜準備】野菜をよく洗って食べやすく切る',
                    '【水切り】野菜の水分をしっかり切る',
                    '【ドレッシング】調味料を混ぜてドレッシングを作る',
                    '【盛り付け】野菜を皿に盛り付ける',
                    '【完成】ドレッシングをかけて完成'
                ],
                'sandwich': [
                    '【パン準備】パンを軽くトーストする',
                    '【具材準備】具材を食べやすく切る',
                    '【調味料】パンに調味料を塗る',
                    '【挟む】具材をパンに挟む',
                    '【カット】食べやすく半分に切って完成'
                ],
                'pasta': [
                    '【パスタ茹で】大きな鍋でパスタを茹でる',
                    '【ソース作り】フライパンでソースを作る',
                    '【具材炒め】具材をソースと一緒に炒める',
                    '【合わせる】茹でたパスタをソースと絡める',
                    '【仕上げ】チーズをかけて完成'
                ],
                'curry': [
                    '【材料カット】すべての材料を大きめに切る',
                    '【炒める】鍋で材料を炒める',
                    '【水を加える】水を加えて煮込む',
                    '【カレールー】カレールーを加えて溶かす',
                    '【煮込み】弱火でとろみがつくまで煮込む'
                ],
                'omelette': [
                    '【卵液作り】卵を溶いて調味料を加える',
                    '【具材準備】具材を小さく切って炒める',
                    '【卵を焼く】フライパンで卵液を焼く',
                    '【具をのせる】半熟状態で具材をのせる',
                    '【包む】半分に折って形を整えて完成'
                ]
            }
            
            base_steps = step_templates.get(cooking_method, step_templates['stir_fry']).copy()
            
            # 気分に応じた調理のコツを追加
            mood_steps = {
                'happy': '【彩り】色鮮やかになるよう盛り付ける',
                'tired': '【優しく】弱火でじっくり調理する',
                'healthy': '【栄養】野菜の栄養を逃さないよう調理する',
                'comfort': '【愛情】じっくり時間をかけて調理する',
                'adventure': '【挑戦】新しいスパイスで味付けする',
                'spicy': '【辛味】お好みで辛さを調整する'
            }
            
            if mood in mood_steps:
                base_steps.insert(-1, mood_steps[mood])
            
            return base_steps
        
        def generate_cooking_tips(cooking_method, mood, protein):
            tips_pool = {
                'stir_fry': [
                    '強火で手早く炒めることで食材のシャキシャキ感を保てます',
                    '調味料は最後に加えて焦げないようにしましょう',
                    '材料は同じ大きさに切ると火の通りが均一になります'
                ],
                'soup': [
                    'アクをしっかり取ると澄んだスープになります',
                    '野菜の甘みを引き出すために弱火でじっくり煮込みましょう',
                    '最後に味を調整することで完璧な味に仕上がります'
                ],
                'rice_dish': [
                    'ご飯は冷めたものを使うとパラパラに仕上がります',
                    '強火で一気に炒めると美味しくなります',
                    '具材に先に味をつけてからご飯と合わせましょう'
                ],
                'noodle': [
                    '麺は表示時間より少し短めに茹でると最適です',
                    'スープは最後に味見をして調整しましょう',
                    '熱いうちに食べるのが一番美味しいです'
                ],
                'grilled': [
                    '最初に強火で表面を焼き、その後中火で火を通します',
                    '肉汁を逃さないよう、あまり触らずに焼きましょう',
                    '焼く前に常温に戻しておくと火が通りやすくなります'
                ],
                'steamed': [
                    '蒸気がしっかり上がってから材料を入れましょう',
                    '蒸し時間は材料の大きさに合わせて調整してください',
                    '蒸した後は余熱で少し置いておくと味が馴染みます'
                ],
                'boiled': [
                    '落し蓋をすることで味が均一に染み込みます',
                    '最初は強火で煮立て、その後弱火でじっくり煮込みます',
                    '煮込み料理は一度冷ますとより味が染み込みます'
                ],
                'salad': [
                    '野菜の水分をしっかり切ることがシャキシャキ感のポイントです',
                    'ドレッシングは食べる直前にかけると野菜がべたつきません',
                    '冷蔵庫で少し冷やすとより美味しくなります'
                ],
                'sandwich': [
                    'パンは軽くトーストすると具材の水分でべたつきません',
                    '具材は水分の少ないものを選ぶと食べやすくなります',
                    'ラップで包んで少し置くと具材が馴染みます'
                ],
                'pasta': [
                    'パスタの茹で汁を少し加えるとソースがよく絡みます',
                    '茹で上がったパスタはすぐにソースと合わせましょう',
                    'チーズは火を止めてから加えると分離しません'
                ],
                'curry': [
                    'ルーを加える前に一度火を止めると ダマになりにくいです',
                    '一度冷ますと味がより深くなります',
                    '野菜は大きめに切ると食べ応えがあります'
                ],
                'omelette': [
                    '卵は完全に固めず、半熟で仕上げるのがポイントです',
                    'バターをしっかり熱してから卵液を入れましょう',
                    '大きくかき混ぜすぎずに優しく扱うのがコツです'
                ]
            }
            
            mood_tips = {
                'happy': '見た目も楽しくなるよう、カラフルに仕上げてください！',
                'tired': '簡単で栄養満点。疲れた体に優しい味です',
                'healthy': '栄養バランスが良く、体に嬉しい一品です',
                'comfort': '懐かしい味で心も体も温まります',
                'adventure': '新しい味の発見を楽しんでください！',
                'spicy': '辛さはお好みで調整して楽しんでください'
            }
            
            method_tips = tips_pool.get(cooking_method, tips_pool['stir_fry'])
            selected_tip = random.choice(method_tips)
            mood_tip = mood_tips.get(mood, '')
            
            return f'{selected_tip}。{mood_tip}'
        
        # メインのレシピ生成ロジック
        ingredient_combinations = get_ingredient_combinations(ingredients)
        all_possible_recipes = []
        
        # 多様なレシピを生成
        for _ in range(20):  # 20個の候補を生成
            combo = random.choice(ingredient_combinations)
            recipe = generate_dynamic_recipe(mood, combo)
            all_possible_recipes.append(recipe)
        
        # 重複を避けて3つ選択
        unique_recipes = []
        used_names = set()
        
        for recipe in all_possible_recipes:
            if recipe['name'] not in used_names and len(unique_recipes) < 3:
                unique_recipes.append(recipe)
                used_names.add(recipe['name'])
        
        # 3つに満たない場合は追加生成
        while len(unique_recipes) < 3:
            combo = random.choice(ingredient_combinations)
            recipe = generate_dynamic_recipe(mood, combo)
            if recipe['name'] not in used_names:
                unique_recipes.append(recipe)
                used_names.add(recipe['name'])
        
        # レシピを文字列形式でフォーマット
        formatted_recipes = f"""【今日の気分】: {mood_name}
【使用可能な食材】: {', '.join(selected_ingredient_names)}

以下、あなたにぴったりの3つのレシピをご提案します：

"""
        
        for i, recipe in enumerate(unique_recipes[:3], 1):
            formatted_recipes += f"""
{i}. **{recipe['name']}**
   ⏰ 調理時間: {recipe['time']}
   📊 難易度: {recipe['difficulty']}
   
   🥘 **材料** ({recipe['serving']})
   ・メイン: {', '.join(recipe['main_ingredients'])}
   ・調味料: {', '.join(recipe['seasonings'])}
   
   👨‍🍳 **作り方**
"""
            for j, step in enumerate(recipe['detailed_steps'], 1):
                formatted_recipes += f"   {j}. {step}\n"
            
            formatted_recipes += f"""
   💡 **コツ・ポイント**
   {recipe['tips']}

---
"""
        
        formatted_recipes += f"\n{mood_name}な今日にぴったりのレシピで、美味しい料理を楽しんでくださいね！🍴✨"
        
        return jsonify({
            'success': True,
            'recipes': formatted_recipes
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