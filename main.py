import flet as ft
import urllib.parse
from datetime import datetime
import sqlite3
import os

# --- إعداد وإدارة قاعدة بيانات SQLite ---
DB_FILE = "deir_algharbi_services.db"

def init_db():
    """إنشاء الجداول إذا لم تكن موجودة مسبقاً لحفظ البيانات بشكل دائم"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # جدول المشتركين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            whatsapp TEXT NOT NULL,
            status TEXT DEFAULT 'approved'
        )
    ''')
    
    # جدول المحلات التجارية والدليل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT DEFAULT 'approved'
        )
    ''')
    
    # جدول دليل الهاتف والوظائف
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone_book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    
    # جدول التنويهات والإعلانات العاجلة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')

    # جدول الشريط الإعلاني المتحرك
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticker_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    ''')

    # جدول خدمات البلدية (المخطط، المقاسم، النظافة، المياه)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS municipality_services (
            service_key TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    # جدول رسائل الدردشة العامة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS public_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')

    # إدخال بيانات افتراضية أولية في حال كانت قاعدة البيانات فارغة تماماً
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES ('khaled', 'المبرمج خالد', '123', '+963944381429', 'approved')")
        cursor.execute("INSERT INTO users VALUES ('ahmed', 'أحمد العلي', '456', '+963944000000', 'approved')")
        
    cursor.execute("SELECT COUNT(*) FROM shops")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO shops (name, type, owner, status) VALUES ('سوبرماركت البركة', 'مواد غذائية', 'المبرمج خالد', 'approved')")
        cursor.execute("INSERT INTO shops (name, type, owner, status) VALUES ('ألبسة النخبة', 'ملابس وأزياء', 'أحمد العلي', 'approved')")
        
    cursor.execute("SELECT COUNT(*) FROM phone_book")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO phone_book (name, phone) VALUES ('المكتب الخدمي للبلدة', '+963944381429')")
        cursor.execute("INSERT INTO phone_book (name, phone) VALUES ('طوارئ الكهرباء', '123')")
        
    cursor.execute("SELECT COUNT(*) FROM announcements")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO announcements (text, time) VALUES ('🚨 تنويه: سيتم قطع التيار الكهربائي اليوم لإجراء أعمال صيانة من الساعة 4 عصراً وحتى 6 مساءً.', '10:00 ص')")

    cursor.execute("SELECT COUNT(*) FROM ticker_ads")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO ticker_ads (text) VALUES ('مرحباً بكم في التطبيق الرسمي الموحد لخدمات دير الغربي.. تابعوا آخر التنويهات العاجلة وجداول البلدية أولاً بأول.')")

    # تهيئة بيانات البلدية الافتراضية
    cursor.execute("SELECT COUNT(*) FROM municipality_services")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO municipality_services VALUES ('layout', 'مخطط البلدة', 'المخطط التنظيمي المعتمد لبلدة دير الغربي لعام 2026 متاح للمراجعة الفنية في مبنى البلدية.')")
        cursor.execute("INSERT INTO municipality_services VALUES ('sectors', 'المقاسم', 'يجري حالياً تنظيم مقاسم التوسع الشمالي الشرقي، يرجى من المالكين مراجعة ديوان البلدية.')")
        cursor.execute("INSERT INTO municipality_services VALUES ('cleaning', 'خدمات النظافة', 'جداول ترحيل النفايات: يومياً من الساعة 6:00 صباحاً وحتى 10:00 صباحاً. يرجى التعاون للحفاظ على النظافة العامة.')")
        cursor.execute("INSERT INTO municipality_services VALUES ('water', 'ضخ المياه', 'جدول ضخ المياه الحالي: الحي الغربي (السبت والإثنين)، الحي الشرقي والوسط (الأحد والأربعاء).')")

    cursor.execute("SELECT COUNT(*) FROM public_chats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO public_chats (sender, username, text, time) VALUES ('المبرمج خالد', 'khaled', 'أهلاً بكم في غرفة الدردشة العامة لأهالي الدير الغربي! 👋', '12:00 م')")

    conn.commit()
    conn.close()

# استدعاء دالة التجهيز قبل تشغيل التطبيق
init_db()

# --- دالات مساعدة للتعامل مع البيانات المستمرة عبر قاعدة البيانات ---
def db_query(query, params=(), commit=False, fetch_all=True):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if commit:
        conn.commit()
        result = cursor.lastrowid if not fetch_all else None
    else:
        result = cursor.fetchall() if fetch_all else cursor.fetchone()
    conn.close()
    return result


def main(page: ft.Page):
    # إزالة القيود الثابتة للشاشات لضمان التوافق التام مع كافة أنواع الجوالات
    page.title = "تطبيق خدمات الدير الغربي"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.rtl = True                
    page.scroll = None  

    my_whatsapp_number = "963944381429" 
    ADMIN_PASSWORD = "1234" 
    
    # المتغيرات المؤقتة في الذاكرة أثناء جلسة التشغيل الحالية
    if not hasattr(page, "current_user"):
        page.current_user = None 
    if not hasattr(page, "online_users"):
        page.online_users = ["khaled"]
    if not hasattr(page, "private_chats"):
        page.private_chats = {}

    # ميكانيزم التحديث التلقائي للدردشة العامة (PubSub)
    def on_broadcast_message(message_data):
        if hasattr(page, "current_view") and page.current_view == "public_chat":
            append_msg_to_ui(message_data)
            
    page.pubsub.subscribe(on_broadcast_message)

    # --- إدارة رسائل الـ SnackBar المضمونة ---
    snack = ft.SnackBar(ft.Text(""))
    page.overlay.append(snack)
    
    def show_message(text):
        snack.content.value = text
        snack.open = True
        page.update()

    # --- شريط التنقل السفلي الاحترافي (متوافق مع عرض الشاشة) ---
    def build_custom_bottom_bar(active_index):
        def make_nav_btn(icon_name, label_text, target_index, on_click_action):
            is_active = (target_index == active_index)
            return ft.GestureDetector(
                on_tap=on_click_action,
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(icon_name, color="green" if is_active else "grey600", size=22),
                        ft.Text(label_text, color="green" if is_active else "grey700", size=10, weight=ft.FontWeight.BOLD if is_active else None)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                    expand=True,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.Container(
            content=ft.Row([
                make_nav_btn(ft.Icons.HOME, "الرئيسية", 0, lambda _: show_main_page()),
                make_nav_btn(ft.Icons.STOREFRONT, "الدليل", 1, lambda _: show_shops_page()),
                make_nav_btn(ft.Icons.CHAT, "الدردشة", 2, lambda _: show_chats_dashboard()),
                make_nav_btn(ft.Icons.PHONE, "الهواتف", 3, lambda _: show_phone_book_page()),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="white", height=60,
            border=ft.Border(top=ft.BorderSide(1, "grey300")), padding=5
        )

    def create_button(text, button_color, on_click_action):
        return ft.Container(
            content=ft.Button(
                content=ft.Row([
                    ft.Text(text, size=16, color="white", weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                style=ft.ButtonStyle(bgcolor=button_color),
                on_click=on_click_action, height=55,
            ),
            expand=True, margin=6 
        )

    def build_header(title_text, on_back_click=None, bg_color="bluegrey800"):
        stack_controls = [
            ft.Container(
                content=ft.Text(title_text, size=18, weight=ft.FontWeight.BOLD, color="white"),
                alignment=ft.Alignment(0, 0), expand=True
            )
        ]
        if on_back_click:
            stack_controls.append(
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK, icon_color="white", icon_size=24, on_click=on_back_click
                    ),
                    left=10, alignment=ft.Alignment(-1, 0)
                )
            )
        return ft.Container(
            content=ft.Stack(stack_controls, height=50), bgcolor=bg_color, padding=10
        )

    def create_shop_card(shop_name, shop_type, shop_owner):
        type_colors = {
            "مواد غذائية": {"bg": "orange50", "text": "orange800", "icon": ft.Icons.LOCAL_GROCERY_STORE},
            "ملابس وأزياء": {"bg": "blue50", "text": "blue800", "icon": ft.Icons.CHECKROOM},
            "صحة وطب": {"bg": "red50", "text": "red800", "icon": ft.Icons.LOCAL_PHARMACY},
        }
        style = type_colors.get(shop_type, {"bg": "grey100", "text": "grey800", "icon": ft.Icons.STORE})

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(style["icon"], color=style["text"], size=26),
                    bgcolor=style["bg"], padding=12, border_radius=10,
                ),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(shop_name, size=16, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(
                        content=ft.Text(shop_type, size=11, color=style["text"], weight=ft.FontWeight.BOLD),
                        bgcolor=style["bg"], padding=5, border_radius=5
                    ),
                    ft.Text(f"👤 إدارة: {shop_owner}", size=11, color="grey600"),
                ], spacing=4, expand=True)
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="white", padding=12, border_radius=12,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color="grey200"), margin=6
        )

    # --- 2. واجهة الصفحة الرئيسية ---
    def show_main_page(e=None):
        page.clean()
        page.current_view = "main"
        
        if page.current_user:
            account_button = ft.TextButton(
                content=ft.Text("🚪 خروج", color="red200", size=14, weight=ft.FontWeight.BOLD),
                on_click=lambda _: [
                    page.online_users.remove(page.current_user["username"]) if page.current_user["username"] in page.online_users else None,
                    setattr(page, 'current_user', None), 
                    show_main_page()
                ]
            )
            user_status = f"👤 {page.current_user['name']}"
        else:
            account_button = ft.TextButton(
                content=ft.Text("🔐 دخول / تسجيل", color="white", size=14, weight=ft.FontWeight.BOLD),
                on_click=show_login_page
            )
            user_status = "🚪 تصفح كـ زائر"
        
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Image(src="sma.jpg", width=36, height=36, fit="cover"),
                            border_radius=18, clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                        ),
                        ft.Text("تطبيق الدير الغربي", size=18, weight=ft.FontWeight.BOLD, color="white"),
                    ], spacing=10),
                    account_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(user_status, size=12, color="white70"),
            ]),
            bgcolor="green", padding=15,
        )

        ticker_banner = ft.Container()
        db_ticker = db_query("SELECT text FROM ticker_ads ORDER BY id DESC LIMIT 1")
        if db_ticker:
            ticker_banner = ft.Container(
                content=ft.Row([
                    ft.Text(db_ticker[0][0], size=13, color="green800", weight=ft.FontWeight.BOLD)
                ], scroll="auto"),
                bgcolor="green50", padding=8, border=ft.Border(bottom=ft.BorderSide(1, "green200"))
            )

        announcement_banner = ft.Container()
        db_announcements = db_query("SELECT text, time FROM announcements ORDER BY id DESC LIMIT 1")
        if db_announcements:
            ann_text, ann_time = db_announcements[0]
            announcement_banner = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CAMPAIGN, color="red800", size=24),
                    ft.VerticalDivider(width=10, color="red300"),
                    ft.Column([
                        ft.Text(ann_text, size=12, color="red900", weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"⏳ أُضيف: {ann_time}", size=9, color="grey600")
                    ], expand=True, spacing=1)
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="red50", padding=10, margin=5, border=ft.Border.all(1, "red200"), border_radius=10
            )

        services_title = ft.Text("الخدمات المتاحة:", size=16, weight=ft.FontWeight.BOLD)
        
        encoded_msg = urllib.parse.quote("السلام عليكم، أريد الاستفسار عن خدمات الدير الغربي")
        whatsapp_url = f"https://wa.me/{my_whatsapp_number}?text={encoded_msg}"

        btn_whatsapp = create_button("💬 التواصل عبر الواتساب", "green", lambda _: page.launch_url(whatsapp_url))
        btn_municipality = create_button("🏛️ بلدية دير الغربي", "bluegrey800", lambda _: show_municipality_page())
        btn_shops = create_button("🛍️ دليل المحلات التجارية", "orange800", lambda _: show_shops_page()) 
        btn_chats = create_button("💬 غرف ومحادثات الدردشة", "bluegrey700", lambda _: show_chats_dashboard())
        btn_phone_book = create_button("📞 دليل الهواتف والوظائف", "blue", lambda _: show_phone_book_page()) 

        footer = ft.Container(
            content=ft.Column([
                ft.Text("تم التطوير بواسطة المبرمج خالد أحمد", size=12, color="grey700"),
                ft.TextButton(content=ft.Text("🔐 لوحة التحكم للمشرف", color="bluegrey400", size=11), on_click=show_admin_login_page)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), margin=15
        )

        scrollable_content = ft.ListView([
            header, ticker_banner, announcement_banner, ft.Container(height=5), ft.Container(content=services_title, padding=10), 
            btn_whatsapp, btn_municipality, btn_shops, btn_chats, btn_phone_book, footer
        ], expand=True, spacing=10)

        # دمج المحتوى المرن مع شريط التنقل السفلي الثابت
        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- قسم واجهة بلدية دير الغربي ---
    def show_municipality_page():
        page.clean()
        page.current_view = "municipality"
        mun_header = build_header("بلدية دير الغربي", on_back_click=lambda _: show_main_page(), bg_color="bluegrey800")

        def show_sub_service(service_key, title_name, icon_widget):
            page.clean()
            sub_header = build_header(title_name, on_back_click=lambda _: show_municipality_page(), bg_color="green800")
            
            db_data = db_query("SELECT content FROM municipality_services WHERE service_key = ?", (service_key,))
            content_text = db_data[0][0] if db_data else "لا توجد بيانات متوفرة حالياً."

            card_content = ft.Container(
                content=ft.Column([
                    ft.Icon(icon_widget, size=40, color="green800"),
                    ft.Container(height=10),
                    ft.Text(title_name, size=18, weight="bold", color="green900"),
                    ft.Divider(color="grey300"),
                    ft.Text(content_text, size=14, color="grey800", text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="white", padding=20, border_radius=12,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color="grey300"), margin=15
            )
            
            page.add(
                ft.Column([
                    ft.ListView([sub_header, ft.Container(height=20), card_content], expand=True),
                    build_custom_bottom_bar(0)
                ], expand=True, spacing=0)
            )
            page.update()

        btn_layout = create_button("🗺️ مخطط البلدة", "teal700", lambda _: show_sub_service("layout", "مخطط البلدة", ft.Icons.MAP))
        btn_sectors = create_button("📐 المقاسم", "brown700", lambda _: show_sub_service("sectors", "المقاسم", ft.Icons.LANDSCAPE))
        btn_cleaning = create_button("🧹 خدمات النظافة", "bluegrey600", lambda _: show_sub_service("cleaning", "خدمات النظافة", ft.Icons.CLEANING_SERVICES))
        btn_water = create_button("💧 ضخ المياه", "blue700", lambda _: show_sub_service("water", "ضخ المياه", ft.Icons.WATER_DROP))

        scrollable_content = ft.ListView([
            mun_header, ft.Container(height=15),
            ft.Container(content=ft.Column([
                btn_layout, btn_sectors, btn_cleaning, btn_water
            ], horizontal_alignment="center"))
        ], expand=True)

        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- 3. واجهة تسجيل الدخول ---
    def show_login_page(e=None):
        page.clean()
        page.current_view = "login"
        login_header = build_header("تسجيل دخول الأعضاء", on_back_click=lambda _: show_main_page(), bg_color="bluegrey800")

        txt_user = ft.TextField(label="اسم المستخدم (مطلوب)")
        txt_pass = ft.TextField(label="كلمة السر (مطلوب)", password=True, can_reveal_password=True)

        def process_login(e):
            username = txt_user.value.strip().lower()
            password = txt_pass.value
            
            if not username or not password:
                show_message("⚠️ يرجى ملء حقل اسم المستخدم وكلمة السر معاً!")
                return

            user_data = db_query("SELECT name, password, status FROM users WHERE username = ?", (username,))
            if user_data:
                name, db_pass, status = user_data[0]
                if db_pass == password:
                    if status == 'approved':
                        page.current_user = {"username": username, "name": name}
                        if username not in page.online_users:
                            page.online_users.append(username)
                        show_main_page()
                    else:
                        show_message("⏳ حسابك قيد المراجعة حالياً من قبل المشرف!")
                else:
                    show_message("❌ كلمة السر خاطئة!")
            else:
                show_message("❌ اسم المستخدم غير مسجل لدينا!")

        btn_login = create_button("🔓 دخول", "green", process_login)
        btn_go_signup = ft.TextButton("ليس لديك حساب؟ تقدم بطلب تسجيل جديد", on_click=show_signup_page)

        scrollable_content = ft.ListView([
            login_header, ft.Container(height=20), 
            ft.Container(content=ft.Column([txt_user, ft.Container(height=5), txt_pass, ft.Container(height=15), btn_login, btn_go_signup], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], expand=True)

        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- 4. واجهة التسجيل الجديد ---
    def show_signup_page(e):
        page.clean()
        page.current_view = "signup"
        signup_header = build_header("طلب تسجيل حساب جديد", on_back_click=lambda _: show_login_page(), bg_color="bluegrey800")

        txt_new_user = ft.TextField(label="اسم المستخدم باللاتيني *")
        txt_new_name = ft.TextField(label="الاسم الكامل للمشترك *")
        txt_new_pass = ft.TextField(label="كلمة السر *", password=True, can_reveal_password=True)
        txt_confirm_pass = ft.TextField(label="تأكيد كلمة السر *", password=True, can_reveal_password=True)
        txt_new_whatsapp = ft.TextField(label="رقم الواتساب مع رمز الدولة *")

        def process_signup(e):
            user = txt_new_user.value.strip().lower()
            name = txt_new_name.value.strip()
            password = txt_new_pass.value
            confirm_password = txt_confirm_pass.value
            whatsapp = txt_new_whatsapp.value.strip()
            
            if not user or not name or not password or not confirm_password or not whatsapp:
                show_message("❌ خطأ: جميع الحقول إجبارية!")
                return
            
            if password != confirm_password:
                show_message("⚠️ خطأ: كلمة السر وتأكيد كلمة السر غير متطابقين!")
                return

            check_exists = db_query("SELECT username FROM users WHERE username = ?", (user,))
            if check_exists:
                show_message("⚠️ اسم المستخدم هذا محجوز مسبقاً!")
            else:
                db_query("INSERT INTO users VALUES (?, ?, ?, ?, 'pending')", (user, name, password, whatsapp), commit=True)
                
                report_text = f"طلب انضمام جديد للتطبيق للتفعيل:\n👤 اليوزر: {user}\n📝 الاسم: {name}\n📱 واتساب: {whatsapp}"
                encoded_report = urllib.parse.quote(report_text)
                page.launch_url(f"https://wa.me/{my_whatsapp_number}?text={encoded_report}")
                
                show_waiting_approval_page()

        btn_register = create_button("📝 إرسال طلب الانضمام للمشرف", "blue", process_signup)
        
        scrollable_content = ft.ListView([
            signup_header, ft.Container(height=15),
            ft.Container(content=ft.Column([txt_new_user, ft.Container(height=5), txt_new_name, ft.Container(height=5), txt_new_pass, ft.Container(height=5), txt_confirm_pass, ft.Container(height=5), txt_new_whatsapp, ft.Container(height=15), btn_register], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], expand=True)

        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    def show_waiting_approval_page():
        page.clean()
        scrollable_content = ft.ListView([
            ft.Container(height=100),
            ft.Container(content=ft.Column([
                ft.Text("⏳", size=60), 
                ft.Text("تم إرسال طلبك بنجاح! 🎉", size=18, weight=ft.FontWeight.BOLD, color="green800"),
                ft.Container(height=10),
                ft.Text("حسابك الآن قيد المراجعة والتدقيق.\nسيقوم المشرف بتفعيل حسابك قريباً جداً.", size=14, text_align="center", color="grey800"),
                ft.Container(height=25),
                create_button("↩️ العودة للرئيسية كـ زائر", "green", lambda _: show_main_page())
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], expand=True)
        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- 5. نظام واجهات الدردشة ---
    def show_chats_dashboard():
        page.clean()
        page.current_view = "chats_dashboard"
        chat_header = build_header("قسم الدردشة والتواصل", on_back_click=lambda _: show_main_page(), bg_color="bluegrey700")
        
        if not page.current_user:
            scrollable_content = ft.ListView([
                chat_header, ft.Container(height=100),
                ft.Container(content=ft.Column([
                    ft.Text("🔒", size=50),
                    ft.Text("الدردشة للأعضاء فقط!", size=18, weight=ft.FontWeight.BOLD, color="red800"),
                    ft.Text("يرجى تسجيل الدخول أو إنشاء حساب للمشاركة في غرف الحوار.", size=13, text_align="center"),
                    ft.Container(height=20),
                    create_button("🔐 تسجيل الدخول الآن", "green", lambda _: show_login_page()),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            ], expand=True)
            page.add(
                ft.Column([
                    scrollable_content,
                    build_custom_bottom_bar(2)
                ], expand=True, spacing=0)
            )
            page.update()
            return

        btn_public_room = create_button("👥 غرفة الدردشة العامة للمجتمع", "bluegrey800", lambda _: show_public_chat_room())
        members_label = ft.Text("💬 ابدأ محادثة خاصة مع عضو:", size=15, weight=ft.FontWeight.BOLD, text_align="right")
        members_list_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        all_approved_users = db_query("SELECT username, name FROM users WHERE status = 'approved'")
        for u_username, u_name in all_approved_users:
            if u_username != page.current_user["username"]:
                members_list_view.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON, color="blue"),
                            title=ft.Text(u_name),
                            subtitle=ft.Text(f"@{u_username}"),
                            trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14),
                            on_click=lambda _, tu=u_username, tn=u_name: show_private_chat_room(tu, tn)
                        ),
                        bgcolor="white", border_radius=10, margin=4,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=3, color="grey200")
                    )
                )

        scrollable_content = ft.ListView([
            chat_header, ft.Container(height=15),
            ft.Container(content=ft.Column([
                btn_public_room, ft.Container(height=15),
                ft.Container(content=members_label, padding=10),
                members_list_view
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], expand=True)
        
        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(2)
            ], expand=True, spacing=0)
        )
        page.update()

    def append_msg_to_ui(msg):
        is_me = (msg["username"] == page.current_user["username"])
        chat_messages_column.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(msg["sender"], size=11, color="bluegrey200" if is_me else "green800", weight=ft.FontWeight.BOLD),
                        ft.Text(msg["text"], size=14, color="white" if is_me else "black"),
                        ft.Text(msg["time"], size=9, color="white60" if is_me else "grey500", text_align="left")
                    ], spacing=2),
                    bgcolor="green700" if is_me else "white", padding=10,
                    border_radius=ft.BorderRadius(12, 12, 2 if is_me else 12, 12 if is_me else 2),
                    width=260, shadow=ft.BoxShadow(spread_radius=1, blur_radius=2, color="grey300")
                )
            ], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START)
        )
        page.update()

    chat_messages_column = ft.Column(scroll="adaptive", expand=True)

    def show_public_chat_room():
        page.clean()
        page.current_view = "public_chat"
        room_header = build_header("الدردشة العامة للبلدة", on_back_click=lambda _: show_chats_dashboard(), bg_color="bluegrey800")
        
        chat_messages_column.controls.clear()
        db_history = db_query("SELECT sender, username, text, time FROM public_chats ORDER BY id ASC")
        for sender, username, text, time in db_history:
            is_me = (username == page.current_user["username"])
            chat_messages_column.controls.append(
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(sender, size=11, color="bluegrey200" if is_me else "green800", weight=ft.FontWeight.BOLD),
                            ft.Text(text, size=14, color="white" if is_me else "black"),
                            ft.Text(time, size=9, color="white60" if is_me else "grey500", text_align="left")
                        ], spacing=2),
                        bgcolor="green700" if is_me else "white", padding=10,
                        border_radius=ft.BorderRadius(12, 12, 2 if is_me else 12, 12 if is_me else 2),
                        width=260, shadow=ft.BoxShadow(spread_radius=1, blur_radius=2, color="grey300")
                    )
                ], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START)
            )

        txt_msg_input = ft.TextField(hint_text="اكتب رسالتك هنا...", expand=True, border_radius=25, height=45)
        
        def send_message(e):
            if not txt_msg_input.value.strip(): return
            now_str = datetime.now().strftime("%I:%M %p").replace("AM","ص").replace("PM","م")
            
            db_query("INSERT INTO public_chats (sender, username, text, time) VALUES (?, ?, ?, ?)",
                     (page.current_user["name"], page.current_user["username"], txt_msg_input.value.strip(), now_str), commit=True)
            
            new_msg = {
                "sender": page.current_user["name"],
                "username": page.current_user["username"],
                "text": txt_msg_input.value.strip(),
                "time": now_str
            }
            page.pubsub.send_all(new_msg)
            txt_msg_input.value = ""
            page.update()
            
        btn_send = ft.IconButton(icon=ft.Icons.SEND, icon_color="green", on_click=send_message)
        input_row = ft.Container(content=ft.Row([txt_msg_input, btn_send]), padding=10, bgcolor="white")
        
        page.add(
            ft.Column([
                room_header, 
                ft.Container(content=chat_messages_column, expand=True, padding=15, bgcolor="grey100"), 
                input_row,
                build_custom_bottom_bar(2)
            ], expand=True, spacing=0)
        )
        page.update()

    def show_private_chat_room(target_username, target_name):
        page.clean()
        page.current_view = "private_chat"
        room_header = build_header(f"محادثة: {target_name}", on_back_click=lambda _: show_chats_dashboard(), bg_color="bluegrey900")
        
        chat_id = "-".join(sorted([page.current_user["username"], target_username]))
        if chat_id not in page.private_chats:
            page.private_chats[chat_id] = []
            
        p_messages_column = ft.Column(scroll="adaptive", expand=True)
        
        def refresh_private_ui():
            p_messages_column.controls.clear()
            for msg in page.private_chats[chat_id]:
                is_me = (msg["username"] == page.current_user["username"])
                p_messages_column.controls.append(
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(msg["text"], size=14, color="white" if is_me else "black"),
                                ft.Text(msg["time"], size=9, color="white60" if is_me else "grey500")
                            ], spacing=2),
                            bgcolor="bluegrey700" if is_me else "white", padding=10,
                            border_radius=ft.BorderRadius(12, 12, 2 if is_me else 12, 12 if is_me else 2),
                            width=260, shadow=ft.BoxShadow(spread_radius=1, blur_radius=2, color="grey300")
                        )
                    ], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START)
                )
            page.update()

        txt_msg_input = ft.TextField(hint_text="اكتب رسالة خاصة...", expand=True, border_radius=25, height=45)
        
        def send_private_message(e):
            if not txt_msg_input.value.strip(): return
            now_str = datetime.now().strftime("%I:%M %p").replace("AM","ص").replace("PM","م")
            new_msg = {"username": page.current_user["username"], "text": txt_msg_input.value.strip(), "time": now_str}
            page.private_chats[chat_id].append(new_msg)
            txt_msg_input.value = ""
            refresh_private_ui()
            
        btn_send = ft.IconButton(icon=ft.Icons.SEND, icon_color="bluegrey700", on_click=send_private_message)
        input_row = ft.Container(content=ft.Row([txt_msg_input, btn_send]), padding=10, bgcolor="white")
        
        refresh_private_ui()
        page.add(
            ft.Column([
                room_header, 
                ft.Container(content=p_messages_column, expand=True, padding=15, bgcolor="grey100"), 
                input_row,
                build_custom_bottom_bar(2)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- 6. واجهة إضافة إعلان تجاري ---
    def show_add_adv_page(e=None):
        page.clean()
        page.current_view = "add_adv"
        adv_header = build_header("إضافة إعلان تجاري معتمد", on_back_click=lambda _: show_shops_page(), bg_color="bluegrey700")

        txt_shop_name = ft.TextField(label="اسم المحل أو الفعالية (مطلوب) *")
        txt_shop_type = ft.Dropdown(
            label="نوع النشاط التجاري *",
            options=[ft.dropdown.Option("مواد غذائية"), ft.dropdown.Option("ملابس وأزياء"), ft.dropdown.Option("صحة وطب"), ft.dropdown.Option("أنشطة تجارية أخرى")]
        )
        txt_shop_owner = ft.TextField(label="الاسم الموثق للمعلن", value=page.current_user["name"] if page.current_user else "", read_only=True)

        def submit_adv(e):
            if not txt_shop_name.value.strip() or not txt_shop_type.value:
                show_message("❌ يرجى ملء اسم المحل واختيار نوع النشاط أولاً!")
                return

            db_query("INSERT INTO shops (name, type, owner, status) VALUES (?, ?, ?, 'pending')",
                     (txt_shop_name.value.strip(), txt_shop_type.value, txt_shop_owner.value, ), commit=True)
            show_message("✅ تم إرسال إعلانك بنجاح بانتظار موافقة المشرف!")
            show_shops_page()

        btn_submit = create_button("🚀 إرسال المنشور للمشرف", "green", submit_adv)
        
        scrollable_content = ft.ListView([
            adv_header, ft.Container(height=15),
            ft.Container(content=ft.Column([txt_shop_name, ft.Container(height=5), txt_shop_type, ft.Container(height=5), txt_shop_owner, ft.Container(height=15), btn_submit], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], expand=True)

        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(1)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- 7. واجهة دليل المحلات التجارية ---
    def show_shops_page(e=None):
        page.clean()
        page.current_view = "shops"
        shops_header = build_header("دليل المحلات التجارية", on_back_click=lambda _: show_main_page(), bg_color="orange800")
        
        if not page.current_user:
            btn_add_adv = create_button("🔒 سجل دخول لإضافة إعلانك مجاناً", "bluegrey400", lambda _: show_login_page())
        else:
            btn_add_adv = create_button("➕ إضافة إعلانك التجاري مجاناً", "bluegrey700", lambda _: show_add_adv_page())
            
        search_field = ft.TextField(label="ابحث عن محل أو تصنيف...", border_color="orange800", on_change=lambda e: filter_shops(e.control.value))
        shops_container = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        def filter_shops(t):
            shops_container.controls.clear()
            active_shops = db_query("SELECT name, type, owner FROM shops WHERE status = 'approved'")
            for name, stype, owner in active_shops:
                if t.lower() in name.lower() or t.lower() in stype.lower(): 
                    shops_container.controls.append(create_shop_card(name, stype, owner))
            page.update()
            
        filter_shops("")
        
        scrollable_content = ft.ListView([
            shops_header, ft.Container(height=5), 
            ft.Container(content=ft.Column([btn_add_adv, ft.Container(height=10), search_field, shops_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], expand=True)

        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(1)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- 8. واجهة دليل الهواتف ووظائف العامة ---
    def show_phone_book_page(e=None):
        page.clean()
        page.current_view = "phone_book"
        phone_header = build_header("دليل الهواتف والوظائف", on_back_click=lambda _: show_main_page(), bg_color="blue")
        
        phone_controls = []
        db_phones = db_query("SELECT name, phone FROM phone_book ORDER BY id DESC")
        for name, phone in db_phones: 
            phone_controls.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(name), subtitle=ft.Text(phone), trailing=ft.Icon(ft.Icons.PHONE, color="blue"), 
                        on_click=lambda _, p=phone: page.launch_url(f"tel:{p}")
                    ), bgcolor="white", border_radius=10, margin=4, shadow=ft.BoxShadow(1, 3, "grey200")
                )
            )
        
        scrollable_content = ft.ListView([phone_header, ft.Container(height=15), ft.Container(content=ft.Column(phone_controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER))], expand=True)
        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(3)
            ], expand=True, spacing=0)
        )
        page.update()

    # --- 9. لوحة تحكم المشرف ---
    def show_admin_login_page(e):
        page.clean()
        page.current_view = "admin_login"
        admin_header = build_header("لوحة دخول المشرف", on_back_click=lambda _: show_main_page(), bg_color="bluegrey900")
        txt_password = ft.TextField(label="أدخل كلمة مرور الإدارة السرية", password=True)
        
        def check_login(e):
            if txt_password.value == ADMIN_PASSWORD: show_admin_panel()
            else: show_message("❌ كلمة المرور خاطئة!")
            
        btn_login = create_button("🔓 دخول المشرف", "green", check_login)
        scrollable_content = ft.ListView([admin_header, ft.Container(height=40), ft.Container(content=ft.Column([txt_password, btn_login], horizontal_alignment=ft.CrossAxisAlignment.CENTER))], expand=True)
        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    def open_edit_dialog(title, fields_dict, on_save_callback):
        page.clean()
        edit_header = build_header(title, on_back_click=lambda _: show_admin_panel(), bg_color="bluegrey700")
        controls_list, inputs_refs = [], {}
        for key, value in fields_dict.items():
            tf = ft.TextField(label=key, value=value)
            inputs_refs[key] = tf
            controls_list.extend([tf, ft.Container(height=5)])
            
        def save_action(e):
            on_save_callback({k: v.value for k, v in inputs_refs.items()})
            show_message("✅ تم الحفظ في قاعدة البيانات!")
            show_admin_panel()
            
        controls_list.append(create_button("💾 حفظ التعديلات", "green", save_action))
        scrollable_content = ft.ListView([edit_header, ft.Container(height=20), ft.Container(content=ft.Column(controls_list, horizontal_alignment=ft.CrossAxisAlignment.CENTER))], expand=True)
        
        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    def show_admin_panel(stats_mode="all"):
        page.clean()
        page.current_view = "admin_panel"
        admin_header = build_header("إدارة تطبيق الدير الغربي", on_back_click=lambda _: show_main_page(), bg_color="bluegrey900")
        
        dynamic_stats_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        def delete_user(un):
            db_query("DELETE FROM users WHERE username = ?", (un,), commit=True)
            if un in page.online_users: page.online_users.remove(un)
            show_message("❌ تم إقصاء الحساب نهائياً!")
            show_admin_panel(stats_mode="subscribers")

        if stats_mode == "subscribers":
            dynamic_stats_view.controls.append(ft.Text("👥 قائمة المشتركين النشطين بالكامل:", size=13, weight=ft.FontWeight.BOLD, color="blue900"))
            all_u = db_query("SELECT username, name, whatsapp FROM users WHERE status = 'approved'")
            for username, name, whatsapp in all_u:
                dynamic_stats_view.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON, color="blue"),
                            ft.Column([ft.Text(name, size=13, weight=ft.FontWeight.BOLD), ft.Text(f"@{username} | 📱 {whatsapp}", size=10, color="grey600")], expand=True),
                            ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, un=username: delete_user(un))
                        ]), bgcolor="blue50", padding=8, border_radius=8, margin=2
                    )
                )
        elif stats_mode == "online":
            dynamic_stats_view.controls.append(ft.Text("🟢 المتصلون حالياً بالبرنامج:", size=13, weight=ft.FontWeight.BOLD, color="green900"))
            for u_name in page.online_users:
                u_info = db_query("SELECT name FROM users WHERE username = ?", (u_name,))
                if u_info:
                    dynamic_stats_view.controls.append(
                        ft.Container(
                            content=ft.Row([ft.Icon(ft.Icons.CIRCLE, color="green", size=12), ft.Text(f"{u_info[0][0]} (@{u_name})", size=13, weight=ft.FontWeight.BOLD)]),
                            bgcolor="green50", padding=10, border_radius=8, margin=2
                        )
                    )

        total_users = db_query("SELECT COUNT(*) FROM users WHERE status = 'approved'")[0][0]
        stats_row = ft.Row([
            ft.GestureDetector(on_tap=lambda _: show_admin_panel("subscribers"), content=ft.Container(content=ft.Column([ft.Text("المشتركين", size=12), ft.Text(str(total_users), size=20, weight="bold")], horizontal_alignment="center"), bgcolor="blue50", padding=10, border_radius=8, expand=True)),
            ft.GestureDetector(on_tap=lambda _: show_admin_panel("online"), content=ft.Container(content=ft.Column([ft.Text("المتصلين", size=12), ft.Text(str(len(page.online_users)), size=20, weight="bold")], horizontal_alignment="center"), bgcolor="green50", padding=10, border_radius=8, expand=True))
        ])

        ticker_manager = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        current_ticker_text = ""
        db_t = db_query("SELECT text FROM ticker_ads ORDER BY id DESC LIMIT 1")
        if db_t: current_ticker_text = db_t[0][0]
        
        txt_ticker_input = ft.TextField(label="نص الشريط الإعلاني المتحرك بالرئيسية", value=current_ticker_text, multiline=True)
        
        def save_ticker_ad(e):
            if txt_ticker_input.value.strip():
                db_query("DELETE FROM ticker_ads")
                db_query("INSERT INTO ticker_ads (text) VALUES (?)", (txt_ticker_input.value.strip(),), commit=True)
                show_message("✅ تم تحديث الشريط الإعلاني المتحرك بالرئيسية!")
                show_admin_panel()

        ticker_manager.controls.extend([txt_ticker_input, ft.Container(height=5), ft.ElevatedButton("💾 تحديث شريط الإعلانات", bgcolor="green", color="white", on_click=save_ticker_ad)])

        announcements_manager = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        txt_announcement_input = ft.TextField(label="اكتب تنويهاً عاجلاً لأهالي البلدة...", multiline=True, height=80)
        
        def publish_announcement(e):
            if not txt_announcement_input.value.strip(): return
            now_str = datetime.now().strftime("%I:%M %p").replace("AM","ص").replace("PM","م")
            db_query("INSERT INTO announcements (text, time) VALUES (?, ?)", ("🚨 " + txt_announcement_input.value.strip(), now_str), commit=True)
            show_admin_panel()
            
        def remove_announcement(aid):
            db_query("DELETE FROM announcements WHERE id = ?", (aid,), commit=True)
            show_admin_panel()

        announcements_list_col = ft.Column()
        db_anns = db_query("SELECT id, text, time FROM announcements ORDER BY id DESC")
        for aid, text, time in db_anns:
            announcements_list_col.controls.append(
                ft.Container(content=ft.Row([ft.Column([ft.Text(text, size=12, weight="bold"), ft.Text(time, size=9)], expand=True), ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, idx=aid: remove_announcement(idx))]), bgcolor="red50", padding=8, border_radius=8, border=ft.Border.all(1, "red200"))
            )
        announcements_manager.controls.extend([txt_announcement_input, ft.Container(height=5), ft.ElevatedButton("🚀 نشر التنويه فوراً", bgcolor="red", color="white", on_click=publish_announcement), ft.Container(height=10), announcements_list_col])

        municipality_manager = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        def edit_mun_service(s_key, s_title, current_content):
            open_edit_dialog(f"تعديل {s_title}", {"تفاصيل القسم / المواعيد": current_content},
                             lambda vals: db_query("UPDATE municipality_services SET content=? WHERE service_key=?", (vals["تفاصيل القسم / المواعيد"], s_key), commit=True))

        db_mun_services = db_query("SELECT service_key, title, content FROM municipality_services")
        for skey, stitle, scontent in db_mun_services:
            municipality_manager.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([ft.Text(stitle, size=14, weight="bold"), ft.Text(scontent, size=11, color="grey600", max_lines=1, overflow="ellipsis")], expand=True),
                        ft.IconButton(ft.Icons.EDIT, icon_color="bluegrey800", on_click=lambda _, sk=skey, st=stitle, sc=scontent: edit_mun_service(sk, st, sc))
                    ]), bgcolor="bluegrey50", padding=8, border_radius=8, margin=2
                )
            )

        user_container = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        pending_u = db_query("SELECT username, name, whatsapp FROM users WHERE status = 'pending'")
        for username, name, whatsapp in pending_u:
            user_container.controls.append(
                ft.Container(content=ft.Column([
                    ft.Text(f"👤 طلب حساب: {name} (@{username})", weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("✅ تفعيل", bgcolor="green", color="white", on_click=lambda _, un=username: [db_query("UPDATE users SET status = 'approved' WHERE username = ?", (un,), commit=True), show_admin_panel()]),
                        ft.ElevatedButton("❌ رفض", bgcolor="red", color="white", on_click=lambda _, un=username: [db_query("DELETE FROM users WHERE username = ?", (un,), commit=True), show_admin_panel()])
                    ], alignment="spaceBetween")
                ]), bgcolor="white", padding=10, border_radius=8, shadow=ft.BoxShadow(1,3,"grey200"))
            )

        shop_pending_container = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        pending_s = db_query("SELECT id, name, type, owner FROM shops WHERE status = 'pending'")
        for sid, name, stype, owner in pending_s:
            shop_pending_container.controls.append(
                ft.Container(content=ft.Column([
                    ft.Text(f"🏪 إعلان معلق: {name} ({stype})", weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("✅ نشر", bgcolor="green", color="white", on_click=lambda _, idx=sid: [db_query("UPDATE shops SET status = 'approved' WHERE id = ?", (idx,), commit=True), show_admin_panel()]),
                        ft.ElevatedButton("❌ رفض", bgcolor="red", color="white", on_click=lambda _, idx=sid: [db_query("DELETE FROM shops WHERE id = ?", (idx,), commit=True), show_admin_panel()])
                    ], alignment="spaceBetween")
                ]), bgcolor="white", padding=10, border_radius=8, shadow=ft.BoxShadow(1,3,"grey200"))
            )

        active_shops_container = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        approved_s = db_query("SELECT id, name, type, owner FROM shops WHERE status = 'approved'")
        
        def edit_shop(sid, current_name, current_type, current_owner):
            open_edit_dialog("تعديل بيانات المحل", {"اسم المحل": current_name, "تصنيف المحل": current_type, "إدارة المحل": current_owner},
                             lambda vals: db_query("UPDATE shops SET name=?, type=?, owner=? WHERE id=?", (vals["اسم المحل"], vals["تصنيف المحل"], vals["إدارة المحل"], sid), commit=True))

        for sid, name, stype, owner in approved_s:
            active_shops_container.controls.append(
                ft.Container(content=ft.Row([
                    ft.Column([ft.Text(name, size=14, weight="bold"), ft.Text(f"تصنيف: {stype} | 👤 {owner}", size=10, color="grey600")], expand=True),
                    ft.IconButton(ft.Icons.EDIT, icon_color="orange800", on_click=lambda _, idx=sid, n=name, t=stype, o=owner: edit_shop(idx, n, t, o)),
                    ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, idx=sid: [db_query("DELETE FROM shops WHERE id = ?", (idx,), commit=True), show_admin_panel()]),
                ]), bgcolor="grey50", padding=8, border_radius=8, margin=2)
            )

        phone_manager_container = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        approved_p = db_query("SELECT id, name, phone FROM phone_book")
        
        def edit_phone(pid, current_name, current_phone):
            open_edit_dialog("تعديل جهة الإتصال", {"المسمى الوظيفي": current_name, "رقم الهاتف": current_phone},
                             lambda vals: db_query("UPDATE phone_book SET name=?, phone=? WHERE id=?", (vals["المسمى الوظيفي"], vals["رقم الهاتف"], pid), commit=True))
                             
        def add_new_phone(e):
            open_edit_dialog("إضافة رقم جديد", {"اسم الجهة": "", "الرقم": ""},
                             lambda vals: db_query("INSERT INTO phone_book (name, phone) VALUES (?, ?)", (vals["اسم الجهة"].strip(), vals["الرقم"].strip()), commit=True) if vals["اسم الجهة"].strip() else None)

        for pid, name, phone in approved_p:
            phone_manager_container.controls.append(
                ft.Container(content=ft.Row([
                    ft.Column([ft.Text(name, size=13, weight="bold"), ft.Text(phone, size=11, color="blue")], expand=True),
                    ft.IconButton(ft.Icons.EDIT, icon_color="orange800", on_click=lambda _, idx=pid, n=name, p=phone: edit_phone(idx, n, p)),
                    ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, idx=pid: [db_query("DELETE FROM phone_book WHERE id = ?", (idx,), commit=True), show_admin_panel()]),
                ]), bgcolor="grey50", padding=8, border_radius=8, margin=2)
            )

        btn_add_phone = ft.TextButton("➕ إضافة رقم جديد إلى دليل الهاتف", icon=ft.Icons.ADD_CALL, on_click=add_new_phone)
        btn_show_all = ft.TextButton("🔄 عرض كافة أقسام الإدارة", icon=ft.Icons.RESTART_ALT, on_click=lambda _: show_admin_panel("all")) if stats_mode != "all" else ft.Container()

        scrollable_content = ft.ListView([
            admin_header, ft.Container(height=10),
            ft.Container(content=ft.Column([
                stats_row, btn_show_all, dynamic_stats_view, ft.Divider(height=25),
                ft.Column([
                    ft.Text("📺 إدارة شريط الإعلانات بالرئيسية:", weight="bold", color="green800", size=14), ticker_manager, ft.Divider(height=25),
                    ft.Text("📢 إدارة التنويهات والإعلانات العاجلة:", weight="bold", color="red800", size=14), announcements_manager, ft.Divider(height=25),
                    ft.Text("🏛️ إدارة خدمات بلدية دير الغربي:", weight="bold", color="bluegrey900", size=14), municipality_manager, ft.Divider(height=25),
                    ft.Text("🔒 طلبات الاشتراك المعلقة:", weight="bold", color="blue800", size=14), user_container, ft.Container(height=10),
                    ft.Text("⏳ طلبات الإعلانات المعلقة:", weight="bold", color="orange800", size=14), shop_pending_container, ft.Divider(height=25),
                    ft.Text("🛍️ إدارة الإعلانات المنشورة الحالية:", weight="bold", color="orange900", size=14), active_shops_container, ft.Divider(height=25),
                    ft.Text("📞 إدارة دليل الهواتف والوظائف:", weight="bold", color="blue900", size=14), btn_add_phone, phone_manager_container,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER) if stats_mode == "all" else ft.Container(),
                ft.Container(height=30)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], expand=True)

        page.add(
            ft.Column([
                scrollable_content,
                build_custom_bottom_bar(0)
            ], expand=True, spacing=0)
        )
        page.update()

    show_main_page()

ft.run(main)
