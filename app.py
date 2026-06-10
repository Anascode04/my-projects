import os
import json
import time
import hashlib
import uuid
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, \
    send_file
from functools import wraps
from werkzeug.utils import secure_filename
from PIL import Image
import io

app = Flask(__name__, template_folder='templates')
app.secret_key = 'akil-brand-secret-key-2024-admin-panel'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
# مسار ملف قاعدة البيانات
PRODUCTS_JSON_PATH = 'data/products.json'
ORDERS_DIR = 'orders'
CONTENT_JSON_PATH = 'data/content.json'
FORMATION_JSON_PATH = 'data/formation.json'  # قاعدة بيانات جديدة للصفحات
UPLOAD_FOLDER = 'static/uploads/products'
UPLOAD_HERO = 'static/uploads/hero'
UPLOAD_SECTIONS = 'static/uploads/sections'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# تأكد من وجود المجلدات
os.makedirs('data', exist_ok=True)
os.makedirs('orders', exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/uploads/logo', exist_ok=True)
os.makedirs(UPLOAD_HERO, exist_ok=True)
os.makedirs(UPLOAD_SECTIONS, exist_ok=True)

# بيانات المشرف الافتراضية
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = hashlib.sha256('Mghogha2004'.encode()).hexdigest()

# قائمة الماركات المتاحة
BRANDS = [
    'Nike',
    'Adidas',
    'Puma',
    'Under Armour',
    'Reebok',
    'New Balance',
    'Jordan',
    'Converse',
    'Vans',
    'Gucci',
    'Prada',
    'Louis Vuitton',
    'Balenciaga',
    'Versace',
    'Armani',
    'Hugo Boss',
    'Calvin Klein',
    'Tommy Hilfiger',
    'Ralph Lauren',
    'Lacoste'
]


# دالة للتحقق من امتدادات الصور المسموح بها
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# تحسين الصور وحفظها
def process_and_save_image(file, max_size=(800, 800), quality=85, folder=UPLOAD_FOLDER):
    if file and allowed_file(file.filename):
        # إنشاء اسم فريد للملف
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(folder, unique_filename)

        # فتح وتعديل الصورة
        try:
            img = Image.open(file)

            # تحويل إلى RGB إذا كان PNG مع شفافية
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img, mask=img)
                img = background

            # تغيير الحجم مع الحفاظ على النسبة
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # حفظ الصورة
            img.save(filepath, 'JPEG', quality=quality, optimize=True)

            # إرجاع المسار النسبي
            return f'/static/uploads/{folder.split("/")[-1]}/{unique_filename}'
        except Exception as e:
            print(f"خطأ في معالجة الصورة: {e}")
            return None
    return None


# حفظ صورة الشعار
def save_logo_image(file):
    if file and allowed_file(file.filename):
        # إنشاء اسم فريد للملف
        filename = secure_filename(file.filename)
        unique_filename = f"logo_{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join('static/uploads/logo', unique_filename)

        # فتح وتعديل الصورة
        try:
            img = Image.open(file)

            # تحويل إلى RGB إذا كان PNG مع شفافية
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img, mask=img)
                img = background

            # تغيير الحجم للحصول على صورة شعار مربعة
            size = min(img.size)
            img = img.crop((0, 0, size, size))
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # حفظ الصورة
            img.save(filepath, 'PNG', optimize=True)

            # إرجاع المسار النسبي
            return f'/static/uploads/logo/{unique_filename}'
        except Exception as e:
            print(f"خطأ في معالجة صورة الشعار: {e}")
            return None
    return None


# حفظ صورة القسم
def save_section_image(file):
    if file and allowed_file(file.filename):
        # إنشاء اسم فريد للملف
        filename = secure_filename(file.filename)
        unique_filename = f"section_{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_SECTIONS, unique_filename)

        # فتح وتعديل الصورة
        try:
            img = Image.open(file)

            # تحويل إلى RGB إذا كان PNG مع شفافية
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img, mask=img)
                img = background

            # تغيير الحجم
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)

            # حفظ الصورة
            img.save(filepath, 'JPEG', quality=95, optimize=True)

            # إرجاع المسار النسبي
            return f'/static/uploads/sections/{unique_filename}'
        except Exception as e:
            print(f"خطأ في معالجة صورة القسم: {e}")
            return None
    return None


# حفظ صورة الهيرو
def save_hero_image(file):
    if file and allowed_file(file.filename):
        # إنشاء اسم فريد للملف
        filename = secure_filename(file.filename)
        unique_filename = f"hero_{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_HERO, unique_filename)

        # فتح وتعديل الصورة
        try:
            img = Image.open(file)

            # تحويل إلى RGB إذا كان PNG مع شفافية
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img, mask=img)
                img = background

            # تغيير الحجم للحصول على صورة مناسبة للهيرو
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

            # حفظ الصورة
            img.save(filepath, 'JPEG', quality=90, optimize=True)

            # إرجاع المسار النسبي
            return f'/static/uploads/hero/{unique_filename}'
        except Exception as e:
            print(f"خطأ في معالجة صورة الهيرو: {e}")
            return None
    return None


# حذف الصورة القديمة
def delete_old_image(image_path):
    try:
        if image_path and image_path.startswith('/static/uploads/'):
            # استخراج المسار الكامل
            parts = image_path.split('/')
            if len(parts) >= 5:
                folder = parts[3]  # مثلا: products, logo, hero, sections
                filename = parts[4]

                if folder == 'products':
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                elif folder == 'logo':
                    filepath = os.path.join('static/uploads/logo', filename)
                elif folder == 'hero':
                    filepath = os.path.join(UPLOAD_HERO, filename)
                elif folder == 'sections':
                    filepath = os.path.join(UPLOAD_SECTIONS, filename)
                else:
                    return

                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"تم حذف الصورة القديمة: {filepath}")
    except Exception as e:
        print(f"خطأ في حذف الصورة: {e}")


# تحميل بيانات المنتجات من JSON
def load_products():
    try:
        if os.path.exists(PRODUCTS_JSON_PATH):
            with open(PRODUCTS_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        print(f"خطأ في تحميل المنتجات: {e}")
        return []


# حفظ المنتجات
def save_products(products):
    try:
        with open(PRODUCTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"خطأ في حفظ المنتجات: {e}")
        return False


# تحميل بيانات المحتوى
def load_content():
    try:
        if os.path.exists(CONTENT_JSON_PATH):
            with open(CONTENT_JSON_PATH, 'r', encoding='utf-8') as f:
                content = json.load(f)
                # ضمان وجود جميع الحقول
                default_content = get_default_content()
                for key in default_content:
                    if key not in content:
                        content[key] = default_content[key]
                return content
        else:
            default_content = get_default_content()
            with open(CONTENT_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, ensure_ascii=False, indent=2)
            return default_content
    except Exception as e:
        print(f"خطأ في تحميل المحتوى: {e}")
        return get_default_content()


def get_default_content():
    """المحتوى الافتراضي للموقع"""
    return {
        "site_title": "Akil Brand",
        "logo_url": "/static/uploads/logo/default_logo.png",

        # قسم الهيرو
        "hero": {
            "background_image": "https://preview.free3d.com/img/2018/10/2400320422412289601/xiwaq15m.jpg",
            "title": "Akil Brand | عالم الفخامة والأناقة الرجالية",
            "subtitle": "وجهتكم الأولى للماركات الرجالية العالمية الفاخرة",
            "button1_text": "استكشاف المجموعات",
            "button2_text": "تسوق الآن"
        },

        # قسم الماركات
        "brands": {
            "subtitle": "شركاؤنا المميزون",
            "title": "الماركات العالمية"
        },

        # قسم المجموعات
        "collections_section": {
            "subtitle": "اكتشف عالم الأناقة",
            "title": "المجموعات الحصرية"
        },
        "collections": [
            {
                "id": "collection_1",
                "title": "مجموعة الفخامة",
                "image": "https://i8.amplience.net/i/jpl/jd_720251_a",
                "description": "قطع حصرية للمناسبات الخاصة",
                "button_text": "استكشاف المجموعة"
            },
            {
                "id": "collection_2",
                "title": "مجموعة الكاجوال",
                "image": "https://www.impulsyn.com/wp-content/uploads/2024/07/taylor-siebert-qmDB3JT9nzU-unsplash-scaled.jpg",
                "description": "أناقة يومية بلمسة عصرية",
                "button_text": "استكشاف المجموعة"
            },
            {
                "id": "collection_3",
                "title": "مجموعة الأعمال",
                "image": "https://i8.amplience.net/i/jpl/jd_725779_a?qlt=92&w=600&h=765&v=1&fmt=auto",
                "description": "احترافية وثقة في العمل",
                "button_text": "استكشاف المجموعة"
            }
        ],

        # قسم المنتجات
        "products_section": {
            "subtitle": "تسوق بتميز",
            "title": "منتجاتنا المختارة",
            "load_more_text": "تحميل المزيد"
        },

        # معلومات الاتصال
        "contact_info": {
            "phone": "+966 50 123 4567",
            "email": "info@akilbrand.com",
            "address": "الرياض، المملكة العربية السعودية"
        },

        # معلومات التذييل
        "footer": {
            "description": "وجهتكم الأولى للماركات الرجالية العالمية الفاخرة. نقدم تشكيلة حصرية من أرقى العلامات التجارية العالمية مع التركيز على الجودة والأناقة والتميز.",
            "newsletter_title": "النشرة البريدية",
            "newsletter_description": "اشترك ليصلك كل جديد عن عروضنا ومنتجاتنا الحصرية."
        }
    }


# حفظ المحتوى
def save_content(content):
    try:
        with open(CONTENT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"خطأ في حفظ المحتوى: {e}")
        return False


# تحميل بيانات الصفحات (FORMATION)
def load_formation():
    try:
        if os.path.exists(FORMATION_JSON_PATH):
            with open(FORMATION_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_formation = {
                "international_shipping": {
                    "title": "الشحن الدولي",
                    "content": """
                    <h2>الشحن الدولي</h2>
                    <p>نقدم خدمة الشحن الدولي إلى جميع دول العالم بأسعار تنافسية وجودة عالية.</p>

                    <h3>مزايا الشحن الدولي:</h3>
                    <ul>
                        <li>شحن سريع إلى معظم الدول</li>
                        <li>تتبع الطلب عبر الإنترنت</li>
                        <li>تأمين على الشحنات</li>
                        <li>خدمة عملاء دولية</li>
                    </ul>

                    <h3>أسعار الشحن:</h3>
                    <ul>
                        <li>الدول العربية: 50-100 دولار (3-7 أيام)</li>
                        <li>أوروبا وأمريكا: 80-150 دولار (5-10 أيام)</li>
                        <li>آسيا وأستراليا: 100-200 دولار (7-14 أيام)</li>
                    </ul>

                    <h3>شروط الشحن الدولي:</h3>
                    <ul>
                        <li>الحد الأدنى للطلب: 200 دولار</li>
                        <li>تخليص جمركي متكامل</li>
                        <li>ضريبة القيمة المضافة حسب الدولة</li>
                        <li>الدفع مقدم باستخدام البطاقات الدولية</li>
                    </ul>
                    """,
                    "last_updated": time.strftime('%Y-%m-%d')
                },
                "exchange_return": {
                    "title": "الاستبدال والاسترجاع",
                    "content": """
                    <h2>سياسة الاستبدال والاسترجاع</h2>
                    <p>نحن نضمن رضاك التام عن منتجاتنا. لدينا سياسة استبدال وإرجاع مرنة لضمان تجربة تسوق ممتازة.</p>

                    <h3>فترة الاسترجاع:</h3>
                    <ul>
                        <li>30 يومًا من تاريخ الاستلام للإرجاع</li>
                        <li>14 يومًا من تاريخ الاستلام للاستبدال</li>
                    </ul>

                    <h3>شروط الاسترجاع:</h3>
                    <ul>
                        <li>المنتج في حالته الأصلية</li>
                        <li>الملصقات والعلامات موجودة</li>
                        <li>المنتج غير مستخدم</li>
                        <li>توفر فاتورة الشراء</li>
                    </ul>

                    <h3>خطوات الاسترجاع:</h3>
                    <ol>
                        <li>اتصل بخدمة العملاء</li>
                        <li>احصل على رقم إذن الإرجاع</li>
                        <li>جهز المنتج للتوصيل</li>
                        <li>استلم المبلغ خلال 5-7 أيام عمل</li>
                    </ol>

                    <h3>الاستثناءات:</h3>
                    <ul>
                        <li>المنتجات الشخصية</li>
                        <li>المنتجات المخصصة حسب الطلب</li>
                        <li>المنتجات المباعة في العروض</li>
                    </ul>
                    """,
                    "last_updated": time.strftime('%Y-%m-%d')
                },
                "customer_support": {
                    "title": "دعم العملاء",
                    "content": """
                    <h2>دعم العملاء</h2>
                    <p>فريق دعم العملاء لدينا جاهز لمساعدتك على مدار الساعة طوال أيام الأسبوع.</p>

                    <h3>قنوات التواصل:</h3>
                    <ul>
                        <li><strong>الهاتف:</strong> +966 50 123 4567</li>
                        <li><strong>الواتساب:</strong> +966 50 123 4567</li>
                        <li><strong>البريد الإلكتروني:</strong> support@akilbrand.com</li>
                        <li><strong>الدردشة المباشرة:</strong> متوفرة على الموقع</li>
                    </ul>

                    <h3>ساعات العمل:</h3>
                    <ul>
                        <li>الأحد - الخميس: 9 صباحًا - 11 مساءً</li>
                        <li>الجمعة - السبت: 1 ظهرًا - 11 مساءً</li>
                    </ul>

                    <h3>خدمات الدعم:</h3>
                    <ul>
                        <li>استفسارات ما قبل الشراء</li>
                        <li>متابعة الطلبات</li>
                        <li>الدعم الفني للموقع</li>
                        <li>شكاوى واستفسارات</li>
                        <li>اقتراحات وتحسينات</li>
                    </ul>

                    <h3>وقت الاستجابة:</h3>
                    <ul>
                        <li>الدردشة المباشرة: فوري</li>
                        <li>البريد الإلكتروني: خلال 24 ساعة</li>
                        <li>الهاتف: خلال 10 دقائق</li>
                    </ul>
                    """,
                    "last_updated": time.strftime('%Y-%m-%d')
                },
                "order_tracking": {
                    "title": "تتبع الطلب",
                    "content": """
                    <h2>تتبع طلبك</h2>
                    <p>يمكنك تتبع طلبك بسهولة من خلال نظام التتبع المتقدم لدينا.</p>

                    <h3>طرق التتبع:</h3>
                    <ul>
                        <li>رقم الطلب</li>
                        <li>رقم الهاتف</li>
                        <li>البريد الإلكتروني</li>
                    </ul>

                    <h3>مراحل التتبع:</h3>
                    <ol>
                        <li><strong>تم استلام الطلب:</strong> تم تأكيد طلبك</li>
                        <li><strong>قيد المعالجة:</strong> جاري تجهيز طلبك</li>
                        <li><strong>جاهز للشحن:</strong> تم تجهيز الطلب</li>
                        <li><strong>تم الشحن:</strong> الطلب في الطريق إليك</li>
                        <li><strong>تم التسليم:</strong> تم استلام الطلب</li>
                    </ol>

                    <h3>معلومات التتبع:</h3>
                    <ul>
                        <li>رقم تتبع الشحنة</li>
                        <li>شركة الشحن</li>
                        <li>التاريخ المتوقع للتسليم</li>
                        <li>سجل التحديثات</li>
                    </ul>

                    <h3>في حالة التأخير:</h3>
                    <p>إذا تأخر طلبك عن الموعد المتوقع، يرجى التواصل مع خدمة العملاء وسنقوم بمتابعة الأمر مع شركة الشحن.</p>
                    """,
                    "last_updated": time.strftime('%Y-%m-%d')
                },
                "faq": {
                    "title": "الأسئلة الشائعة",
                    "content": """
                    <h2>الأسئلة الشائعة</h2>

                    <h3>المنتجات والجودة:</h3>
                    <div class="faq-item">
                        <h4>هل المنتجات أصلية؟</h4>
                        <p>نعم، جميع منتجاتنا أصلية 100% ومضمونة مع فواتير الشراء الرسمية.</p>
                    </div>

                    <div class="faq-item">
                        <h4>ما هي فترة الضمان؟</h4>
                        <p>جميع المنتجات تحمل ضمان 6 أشهر ضد عيوب الصناعة.</p>
                    </div>

                    <h3>الطلبات والشحن:</h3>
                    <div class="faq-item">
                        <h4>كم تستغرق مدة الشحن؟</h4>
                        <p>الشحن داخل المدينة: 1-2 يوم عمل<br>الشحن بين المدن: 2-4 أيام عمل<br>الشحن الدولي: 5-14 يوم عمل</p>
                    </div>

                    <div class="faq-item">
                        <h4>هل الشحن مجاني؟</h4>
                        <p>نعم، الشحن مجاني للطلبات فوق 500 ريال داخل المملكة.</p>
                    </div>

                    <h3>الدفع والأمان:</h3>
                    <div class="faq-item">
                        <h4>ما هي طرق الدفع المتاحة؟</h4>
                        <p>نقبل الدفع نقداً عند الاستلام، وبطاقات الائتمان، والتحويل البنكي، و Apple Pay.</p>
                    </div>

                    <div class="faq-item">
                        <h4>هل بياناتي آمنة؟</h4>
                        <p>نعم، نستخدم أحدث أنظمة التشفير لحماية بياناتك الشخصية والمالية.</p>
                    </div>

                    <h3>الاستبدال والإرجاع:</h3>
                    <div class="faq-item">
                        <h4>ما هي سياسة الإرجاع؟</h4>
                        <p>يمكنك إرجاع المنتج خلال 30 يومًا من تاريخ الاستلام بشرط أن يكون بحالته الأصلية.</p>
                    </div>

                    <div class="faq-item">
                        <h4>كم تستغرق عملية استرداد المبلغ؟</h4>
                        <p>تستغرق عملية استرداد المبلغ من 5 إلى 7 أيام عمل بعد استلام المنتج.</p>
                    </div>
                    """,
                    "last_updated": time.strftime('%Y-%m-%d')
                }
            }
            with open(FORMATION_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_formation, f, ensure_ascii=False, indent=2)
            return default_formation
    except Exception as e:
        print(f"خطأ في تحميل بيانات الصفحات: {e}")
        return {}


# حفظ بيانات الصفحات
def save_formation(formation):
    try:
        with open(FORMATION_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(formation, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"خطأ في حفظ بيانات الصفحات: {e}")
        return False


# تحميل الطلبات
def load_orders():
    orders = []
    try:
        if os.path.exists(ORDERS_DIR):
            for filename in os.listdir(ORDERS_DIR):
                if filename.endswith('.json'):
                    with open(os.path.join(ORDERS_DIR, filename), 'r', encoding='utf-8') as f:
                        order = json.load(f)
                        orders.append(order)
    except Exception as e:
        print(f"خطأ في تحميل الطلبات: {e}")
    return sorted(orders, key=lambda x: x.get('timestamp', ''), reverse=True)


# ديكورات التحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    """الصفحة الرئيسية للموقع"""
    content = load_content()
    return render_template('index.html',
                          site_title=content.get('site_title', 'Akil Brand'),
                          logo_url=content.get('logo_url', '/static/uploads/logo/default_logo.png'))


@app.route('/admin')
@login_required
def admin_dashboard():
    """لوحة التحكم الإدارية"""
    content = load_content()
    return render_template('admin.html',
                          site_title=content.get('site_title', 'Akil Brand'),
                          logo_url=content.get('logo_url', '/static/uploads/logo/default_logo.png'),
                          brands=BRANDS)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """تسجيل الدخول للمشرف"""
    if request.method == 'GET':
        content = load_content()
        return render_template('admin.html',
                              site_title=content.get('site_title', 'Akil Brand'),
                              logo_url=content.get('logo_url', '/static/uploads/logo/default_logo.png'),
                              brands=BRANDS)

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
        session['admin_logged_in'] = True
        session['admin_username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401


@app.route('/admin/logout')
def admin_logout():
    """تسجيل الخروج"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return jsonify({'success': True})


@app.route('/admin/check-auth')
def check_auth():
    """التحقق من حالة تسجيل الدخول"""
    if 'admin_logged_in' in session:
        return jsonify({'logged_in': True, 'username': session.get('admin_username')})
    return jsonify({'logged_in': False})


@app.route('/admin/stats')
@login_required
def get_stats():
    """الحصول على إحصائيات لوحة التحكم"""
    products = load_products()

    # حساب الإجماليات
    products_with_offers = sum(1 for product in products if product.get('sale_price'))
    available_products = sum(1 for product in products if product.get('stock', 0) > 0)
    unique_brands = len(set(product.get('brand') for product in products if product.get('brand')))

    return jsonify({
        'products_count': len(products),
        'offers_count': products_with_offers,
        'available_products': available_products,
        'unique_brands': unique_brands
    })


@app.route('/admin/get-products')
@login_required
def admin_get_products():
    """الحصول على جميع المنتجات للإدارة"""
    products = load_products()
    return jsonify(products)


@app.route('/admin/upload-image', methods=['POST'])
@login_required
def upload_image():
    """رفع صورة جديدة"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'لم يتم اختيار صورة'}), 400

        if file and allowed_file(file.filename):
            image_url = process_and_save_image(file)
            if image_url:
                return jsonify({
                    'success': True,
                    'image_url': image_url,
                    'message': 'تم رفع الصورة بنجاح'
                })
            else:
                return jsonify({'success': False, 'message': 'حدث خطأ في معالجة الصورة'}), 500
        else:
            return jsonify({'success': False, 'message': 'نوع الملف غير مدعوم'}), 400

    except Exception as e:
        print(f"خطأ في رفع الصورة: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/upload-logo', methods=['POST'])
@login_required
def upload_logo():
    """رفع شعار جديد"""
    try:
        if 'logo' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة شعار'}), 400

        file = request.files['logo']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'لم يتم اختيار صورة شعار'}), 400

        if file and allowed_file(file.filename):
            logo_url = save_logo_image(file)
            if logo_url:
                return jsonify({
                    'success': True,
                    'logo_url': logo_url,
                    'message': 'تم رفع الشعار بنجاح'
                })
            else:
                return jsonify({'success': False, 'message': 'حدث خطأ في معالجة الشعار'}), 500
        else:
            return jsonify({'success': False, 'message': 'نوع الملف غير مدعوم'}), 400

    except Exception as e:
        print(f"خطأ في رفع الشعار: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/upload-hero', methods=['POST'])
@login_required
def upload_hero():
    """رفع صورة الهيرو"""
    try:
        if 'hero' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة هيرو'}), 400

        file = request.files['hero']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'لم يتم اختيار صورة هيرو'}), 400

        if file and allowed_file(file.filename):
            hero_url = save_hero_image(file)
            if hero_url:
                return jsonify({
                    'success': True,
                    'image_url': hero_url,
                    'message': 'تم رفع صورة الهيرو بنجاح'
                })
            else:
                return jsonify({'success': False, 'message': 'حدث خطأ في معالجة صورة الهيرو'}), 500
        else:
            return jsonify({'success': False, 'message': 'نوع الملف غير مدعوم'}), 400

    except Exception as e:
        print(f"خطأ في رفع صورة الهيرو: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/upload-section', methods=['POST'])
@login_required
def upload_section():
    """رفع صورة قسم"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'لم يتم اختيار صورة'}), 400

        if file and allowed_file(file.filename):
            section_url = save_section_image(file)
            if section_url:
                return jsonify({
                    'success': True,
                    'image_url': section_url,
                    'message': 'تم رفع صورة القسم بنجاح'
                })
            else:
                return jsonify({'success': False, 'message': 'حدث خطأ في معالجة صورة القسم'}), 500
        else:
            return jsonify({'success': False, 'message': 'نوع الملف غير مدعوم'}), 400

    except Exception as e:
        print(f"خطأ في رفع صورة القسم: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/delete-image', methods=['POST'])
@login_required
def delete_image():
    """حذف صورة"""
    try:
        data = request.get_json()
        image_url = data.get('image_url')

        if image_url:
            delete_old_image(image_url)
            return jsonify({'success': True, 'message': 'تم حذف الصورة'})
        else:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400

    except Exception as e:
        print(f"خطأ في حذف الصورة: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/save-product', methods=['POST'])
@login_required
def admin_save_product():
    """حفظ منتج جديد أو تعديله"""
    try:
        product_data = request.get_json()
        products = load_products()

        # حذف الصور القديمة إذا كان تعديلاً
        if 'id' in product_data and product_data['id']:
            product_id = int(product_data['id'])
            old_product = next((p for p in products if p['id'] == product_id), None)
            if old_product:
                # حذف الصور القديمة إذا تم تغييرها
                if 'old_images' in product_data and product_data['old_images']:
                    old_images = set(old_product.get('images', []))
                    new_images = set(product_data.get('images', []))
                    deleted_images = old_images - new_images
                    for img in deleted_images:
                        delete_old_image(img)

                # حذف الصورة الرئيسية القديمة إذا تم تغييرها
                if 'old_main_image' in product_data and product_data['old_main_image']:
                    if product_data['old_main_image'] != product_data.get('image'):
                        delete_old_image(product_data['old_main_image'])

        if 'id' in product_data and product_data['id']:
            # تحديث منتج موجود
            product_id = int(product_data['id'])
            for i, product in enumerate(products):
                if product['id'] == product_id:
                    products[i] = product_data
                    break
            else:
                # إذا لم يوجد المنتج، أضفه جديداً
                product_data['id'] = len(products) + 1
                products.append(product_data)
        else:
            # إضافة منتج جديد
            product_data['id'] = len(products) + 1
            products.append(product_data)

        # حفظ المنتجات
        if save_products(products):
            return jsonify({'success': True, 'message': 'تم حفظ المنتج بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'حدث خطأ في الحفظ'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/delete-product/<int:product_id>', methods=['DELETE'])
@login_required
def admin_delete_product(product_id):
    """حذف منتج"""
    try:
        products = load_products()
        product_to_delete = next((p for p in products if p['id'] == product_id), None)

        if product_to_delete:
            # حذف جميع صور المنتج
            for img in product_to_delete.get('images', []):
                delete_old_image(img)

            # حذف الصورة الرئيسية
            if product_to_delete.get('image'):
                delete_old_image(product_to_delete['image'])

        # حذف المنتج من القائمة
        products = [p for p in products if p['id'] != product_id]

        if save_products(products):
            return jsonify({'success': True, 'message': 'تم حذف المنتج بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'حدث خطأ في الحذف'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/get-content')
@login_required
def admin_get_content():
    """الحصول على محتوى الموقع"""
    content = load_content()
    return jsonify(content)


@app.route('/api/content')
def get_content():
    """API للحصول على محتوى الموقع"""
    content = load_content()
    return jsonify(content)


@app.route('/admin/save-content', methods=['POST'])
@login_required
def admin_save_content():
    """حفظ محتوى الموقع"""
    try:
        content_data = request.get_json()
        current_content = load_content()

        # تحديث المحتوى
        current_content.update(content_data)

        if save_content(current_content):
            return jsonify({'success': True, 'message': 'تم حفظ المحتوى بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'حدث خطأ في الحفظ'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/get-formation')
@login_required
def admin_get_formation():
    """الحصول على بيانات الصفحات"""
    formation = load_formation()
    return jsonify(formation)


@app.route('/admin/save-formation/<page_id>', methods=['POST'])
@login_required
def admin_save_formation(page_id):
    """حفظ بيانات صفحة معينة"""
    try:
        page_data = request.get_json()
        formation = load_formation()

        # التحقق من وجود المعرف
        if page_id not in formation:
            return jsonify({'success': False, 'message': 'معرف الصفحة غير موجود'}), 404

        # تحديث بيانات الصفحة
        formation[page_id].update(page_data)

        if save_formation(formation):
            return jsonify({'success': True, 'message': 'تم حفظ الصفحة بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'حدث خطأ في الحفظ'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/save-branding', methods=['POST'])
@login_required
def admin_save_branding():
    """حفظ بيانات الهوية والعلامة"""
    try:
        branding_data = request.get_json()
        current_content = load_content()

        # تحديث بيانات الهوية
        if 'site_title' in branding_data:
            current_content['site_title'] = branding_data['site_title']

        if 'logo_url' in branding_data:
            current_content['logo_url'] = branding_data['logo_url']

        if save_content(current_content):
            return jsonify({'success': True, 'message': 'تم حفظ بيانات الهوية بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'حدث خطأ في الحفظ'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# APIs للواجهة الأمامية
@app.route('/api/products')
def get_products():
    """API للحصول على قائمة المنتجات من قاعدة البيانات JSON"""
    try:
        products = load_products()

        # تحقق من تاريخ انتهاء العرض وتحديث حالة المنتج إذا لزم
        current_date = time.strftime('%Y-%m-%d')
        updated = False

        for product in products:
            if product.get('sale_end_date'):
                if product['sale_end_date'] < current_date:
                    # العرض انتهى، قم بإزالته
                    if 'sale_price' in product:
                        del product['sale_price']
                    if 'sale_end_date' in product:
                        del product['sale_end_date']
                    updated = True

        # إذا تم تحديث المنتجات، احفظها
        if updated:
            save_products(products)

        return jsonify(products)
    except Exception as e:
        print(f"❌ خطأ في تحميل المنتجات: {e}")
        return jsonify({"error": "خطأ في تحميل المنتجات"}), 500


@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """API للحصول على منتج معين"""
    try:
        products = load_products()
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            return jsonify(product)
        else:
            return jsonify({"error": "المنتج غير موجود"}), 404
    except Exception as e:
        print(f"❌ خطأ في تحميل المنتج: {e}")
        return jsonify({"error": "خطأ في تحميل المنتج"}), 500


@app.route('/api/formation')
def get_formation():
    """API للحصول على بيانات الصفحات"""
    try:
        formation = load_formation()
        return jsonify(formation)
    except Exception as e:
        print(f"❌ خطأ في تحميل بيانات الصفحات: {e}")
        return jsonify({"error": "خطأ في تحميل بيانات الصفحات"}), 500


@app.route('/api/formation/<page_id>')
def get_formation_page(page_id):
    """API للحصول على صفحة معينة"""
    try:
        formation = load_formation()
        page_data = formation.get(page_id)

        if page_data:
            return jsonify(page_data)
        else:
            return jsonify({"error": "الصفحة غير موجودة"}), 404
    except Exception as e:
        print(f"❌ خطأ في تحميل الصفحة: {e}")
        return jsonify({"error": "خطأ في تحميل الصفحة"}), 500


@app.route('/checkout', methods=['POST'])
def checkout():
    """API لتلقي طلبات الشراء"""
    try:
        # الحصول على البيانات من الطلب
        data = request.json

        # في التطبيق الحقيقي، هنا يتم حفظ الطلب في قاعدة البيانات
        # وإرسال إشعارات للعمولاء والإدارة

        # بيانات الطلب الأساسية
        order_data = {
            'order_id': f"AKIL-{int(time.time())}",
            'full_name': data.get('full_name'),
            'phone': data.get('phone'),
            'city': data.get('city'),
            'district': data.get('district'),
            'payment_method': data.get('payment_method'),
            'total': data.get('total'),
            'items': data.get('items', []),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # حفظ الطلب في ملف (في التطبيق الحقيقي يستخدم قاعدة بيانات)
        save_order_to_file(order_data)

        return jsonify({
            'success': True,
            'message': 'تم استلام الطلب بنجاح',
            'order_id': order_data['order_id']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        }), 400


def save_order_to_file(order_data):
    """حفظ الطلب في ملف JSON (لأغراض العرض فقط)"""
    try:
        # حفظ الطلب في ملف
        filename = f"{ORDERS_DIR}/{order_data['order_id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(order_data, f, ensure_ascii=False, indent=2)

        print(f"✅ تم حفظ الطلب: {order_data['order_id']}")

    except Exception as e:
        print(f"❌ خطأ في حفظ الطلب: {e}")


# تقديم الملفات الثابتة
@app.route('/static/uploads/logo/<path:filename>')
def serve_logo(filename):
    return send_from_directory('static/uploads/logo', filename)


@app.route('/static/uploads/products/<path:filename>')
def serve_product_image(filename):
    return send_from_directory('static/uploads/products', filename)


@app.route('/static/uploads/hero/<path:filename>')
def serve_hero_image(filename):
    return send_from_directory('static/uploads/hero', filename)


@app.route('/static/uploads/sections/<path:filename>')
def serve_section_image(filename):
    return send_from_directory('static/uploads/sections', filename)


# إنشاء شعار افتراضي إذا لم يكن موجوداً
def create_default_logo():
    logo_path = 'static/uploads/logo/default_logo.png'
    if not os.path.exists(logo_path):
        try:
            # إنشاء شعار بسيط
            img = Image.new('RGB', (200, 200), color=(212, 175, 55))

            # إضافة نص A
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)

            # استخدام خط افتراضي
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()

            # رسم الحرف A
            draw.text((100, 100), "A", fill=(255, 255, 255), font=font, anchor="mm")

            # حفظ الصورة
            img.save(logo_path, 'PNG')
            print(f"✅ تم إنشاء الشعار الافتراضي: {logo_path}")
        except Exception as e:
            print(f"❌ خطأ في إنشاء الشعار الافتراضي: {e}")


if __name__ == '__main__':
    # إنشاء ملف المنتجات إذا لم يكن موجوداً
    if not os.path.exists(PRODUCTS_JSON_PATH):
        with open(PRODUCTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"📁 تم إنشاء ملف المنتجات الفارغ: {PRODUCTS_JSON_PATH}")

    # إنشاء ملف المحتوى إذا لم يكن موجوداً
    load_content()  # هذا سيُنشئ الملف إذا لم يكن موجوداً

    # إنشاء ملف الصفحات إذا لم يكن موجوداً
    load_formation()  # هذا سيُنشئ الملف إذا لم يكن موجوداً

    # إنشاء شعار افتراضي
    create_default_logo()

    print("🚀 بدء تشغيل متجر Akil Brand...")
    print("📖 افتح المتصفح واذهب إلى: http://localhost:5000")
    print("🔐 لوحة التحكم: http://localhost:5000/admin")
    print("👤 بيانات الدخول: admin / admin123")
    print("🏷️  الميزات الجديدة:")
    print("   - نظام إدارة المحتوى المتكامل")
    print("   - التحكم في صور ونصوص الأقسام الرئيسية")
    print("   - إدارة المجموعات الحصرية")
    print("   - إضافة/حذف/تعديل جميع النصوص والصور")
    print("📂 مسار قاعدة بيانات المنتجات:", PRODUCTS_JSON_PATH)
    print("📂 مسار قاعدة بيانات الصفحات:", FORMATION_JSON_PATH)
    print("📂 مسار قاعدة بيانات المحتوى:", CONTENT_JSON_PATH)
    print("📸 مسار تخزين الصور:", UPLOAD_FOLDER)
    print("🏷️ مسار تخزين الشعارات: static/uploads/logo/")
    print("🌅 مسار تخزين صور الهيرو: static/uploads/hero/")
    app.run(debug=True, port=5000)