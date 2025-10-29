import streamlit as st
from google import genai
from google.genai import types
import fitz  # PyMuPDF
import re
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions
import os

# تنظیمات صفحه
st.set_page_config(
    page_title="سامانه دستیار نظرات مشورتی حقوقی",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key ثابت
GEMINI_API_KEY = "AIzaSyDyj1DlOLAlbKzTLFP2tz95TcIca4oV0Vg"

# استایل CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background: #ffffff;
    }
    
    .main-header {
        background: linear-gradient(120deg, #2c3e50, #3498db);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin-top: 1rem;
        opacity: 0.95;
    }
    
    .card {
        background: #f8f9fa;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
        direction: rtl;
    }
    
    .card h2 {
        color: #2c3e50;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 1.5rem;
        text-align: right;
        border-right: 5px solid #3498db;
        padding-right: 15px;
    }
    
    .info-box {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: right;
        font-size: 1.1rem;
        line-height: 1.8;
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
    }
    
    .info-box h4 {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: right;
        font-size: 1.1rem;
    }
    
    .question-card {
        background: #ffffff;
        border: 2px solid #3498db;
        color: #2c3e50;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.2);
    }
    
    .question-card h4 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #3498db;
    }
    
    .answer-section {
        background: #ffffff;
        border: 2px solid #27ae60;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(39, 174, 96, 0.2);
    }
    
    .answer-section h4 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #27ae60;
    }
    
    .summary-section {
        background: #ffffff;
        border: 2px solid #9b59b6;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(155, 89, 182, 0.2);
    }
    
    .summary-section h4 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #9b59b6;
    }
    
    .relevance-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .high-relevance {
        background: #27ae60;
        color: white;
    }
    
    .medium-relevance {
        background: #f39c12;
        color: white;
    }
    
    .low-relevance {
        background: #95a5a6;
        color: white;
    }
    
    .document-view {
        background: #f8f9fa;
        border: 2px solid #3498db;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        max-height: 500px;
        overflow-y: auto;
        direction: rtl;
        text-align: right;
    }
    
    .document-view h5 {
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    .document-view p {
        color: #495057;
        line-height: 2;
        margin: 1rem 0;
        padding: 0.5rem;
        background: white;
        border-radius: 5px;
    }
    
    .source-item {
        background: white;
        border: 2px solid #e9ecef;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .source-item:hover {
        border-color: #3498db;
        box-shadow: 0 3px 10px rgba(52, 152, 219, 0.2);
    }
    
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(17, 153, 142, 0.4);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2.5rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1.2rem;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        direction: rtl;
        text-align: right;
        font-family: 'Vazirmatn', sans-serif;
        font-size: 1.1rem;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        background: white;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(240, 147, 251, 0.4);
    }
    
    .stat-number {
        font-size: 3.5rem;
        font-weight: 800;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .element-container, .stMarkdown, p, h1, h2, h3, h4, h5, h6, div, span {
        direction: rtl !important;
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# دیتابیس پیشرفته با Sentence Transformers
class AdvancedLegalDatabase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./legal_db_advanced")
        
        # استفاده از embedding function پیشرفته
        # از مدل multilingual برای پشتیبانی بهتر از فارسی
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-mpnet-base-v2"
        )
        
        try:
            self.collection = self.client.get_collection(
                name="legal_inquiries_semantic",
                embedding_function=self.embedding_function
            )
        except:
            self.collection = self.client.create_collection(
                name="legal_inquiries_semantic",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_document(self, doc_data):
        """افزودن سند با embedding معنایی"""
        doc_id = f"{doc_data['شماره_نامه']}_{doc_data['تاریخ']}".replace('/', '_').replace(' ', '_')
        
        # ساخت متن کامل برای embedding بهتر
        full_text = f"""
استعلام: {doc_data['استعلام']}
پاسخ: {doc_data['پاسخ']}
شماره پرونده: {doc_data['شماره_پرونده']}
"""
        
        try:
            self.collection.upsert(
                documents=[full_text],
                metadatas=[doc_data],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            st.error(f"خطا در ذخیره سند: {str(e)}")
            return False
    
    def semantic_search(self, query, n_results=5):
        """جستجوی معنایی پیشرفته"""
        try:
            count = self.collection.count()
            if count == 0:
                return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
            
            # جستجوی معنایی با cosine similarity
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
                include=['documents', 'metadatas', 'distances']
            )
            
            return results
        except Exception as e:
            st.error(f"خطا در جستجو: {str(e)}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def get_all_count(self):
        try:
            return self.collection.count()
        except:
            return 0

# پارسر PDF
class PDFExtractor:
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    
    @staticmethod
    def parse_simple(text):
        documents = []
        signature_patterns = ['دکتر احمد محمدی باردئی', 'دكتر احمد محمدي باردئي']
        
        parts = [text]
        for pattern in signature_patterns:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(pattern))
            parts = new_parts
        
        st.info(f"🔍 تعداد بخش‌های پیدا شده: {len(parts)} بخش")
        
        for idx, part in enumerate(parts):
            if len(part.strip()) < 100:
                continue
            
            try:
                date_matches = re.findall(r'\d{4}/\d{1,2}/\d{1,2}', part)
                if not date_matches:
                    continue
                date = date_matches[0]
                
                number_matches = re.findall(r'\d+/\d+/\d+', part)
                if len(number_matches) < 1:
                    continue
                number = number_matches[0] if number_matches[0] != date else (number_matches[1] if len(number_matches) > 1 else number_matches[0])
                
                case_match = re.search(r'شماره پرونده\s*:?\s*([^\n]+)', part)
                case_number = case_match.group(1).strip() if case_match else "نامشخص"
                
                inquiry_match = re.search(r'استعلام\s*:?\s*(.*?)\s*(?:پاسخ|ﭘاسﺦ)', part, re.DOTALL | re.IGNORECASE)
                inquiry = inquiry_match.group(1).strip() if inquiry_match else ""
                
                answer_match = re.search(r'(?:پاسخ|ﭘاسﺦ)\s*:?\s*(.*)', part, re.DOTALL | re.IGNORECASE)
                answer = answer_match.group(1).strip() if answer_match else ""
                
                inquiry = re.sub(r'\s+', ' ', inquiry).strip()
                answer = re.sub(r'\s+', ' ', answer).strip()
                
                if len(inquiry) < 20 or len(answer) < 20:
                    continue
                
                doc = {
                    'تاریخ': date,
                    'شماره_نامه': number,
                    'شماره_پرونده': case_number,
                    'استعلام': inquiry,
                    'پاسخ': answer,
                    'پاسخ_دهنده': 'دکتر احمد محمدی باردئی'
                }
                
                documents.append(doc)
                st.success(f"✅ سند {idx+1} - تاریخ: {date} - شماره: {number}")
                
            except Exception as e:
                continue
        
        return documents

# RAG پیشرفته با Semantic Search - نسخه بهبود یافته
class AdvancedLegalRAG:
    def __init__(self):
        self.db = AdvancedLegalDatabase()
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def calculate_relevance_score(self, distance):
        """محاسبه درصد ارتباط بر اساس فاصله cosine"""
        # فاصله کمتر = ارتباط بیشتر
        # فاصله cosine بین 0 تا 2 است
        relevance = max(0, 100 - (distance * 50))
        return round(relevance, 1)
    
    def get_relevance_category(self, score):
        """دسته‌بندی میزان ارتباط"""
        if score >= 80:
            return "high-relevance", "🟢 ارتباط بسیار بالا"
        elif score >= 60:
            return "medium-relevance", "🟡 ارتباط متوسط"
        else:
            return "low-relevance", "🔴 ارتباط پایین"
    
    def generate_answer(self, question):
        """تولید پاسخ با RAG پیشرفته - نسخه بهبود یافته"""
        
        # جستجوی معنایی
        st.info("🔍 در حال جستجوی معنایی در پایگاه داده...")
        search_results = self.db.semantic_search(question, n_results=5)
        
        if not search_results['documents'][0]:
            return None, None, []
        
        # تحلیل نتایج و فیلتر بر اساس relevance
        filtered_sources = []
        for i, (doc, meta, distance) in enumerate(zip(
            search_results['documents'][0],
            search_results['metadatas'][0],
            search_results['distances'][0]
        )):
            relevance_score = self.calculate_relevance_score(distance)
            
            # فقط اسناد با ارتباط بالاتر از 50% را نگه دار
            if relevance_score >= 50:
                filtered_sources.append({
                    'index': i + 1,
                    'document': doc,
                    'metadata': meta,
                    'distance': distance,
                    'relevance_score': relevance_score,
                    'شماره_نامه': meta.get('شماره_نامه'),
                    'تاریخ': meta.get('تاریخ'),
                    'شماره_پرونده': meta.get('شماره_پرونده'),
                    'استعلام': meta.get('استعلام'),
                    'پاسخ': meta.get('پاسخ'),
                    'پاسخ_دهنده': meta.get('پاسخ_دهنده')
                })
        
        if not filtered_sources:
            st.warning("⚠️ هیچ سند مرتبطی با ارتباط کافی پیدا نشد")
            return None, None, []
        
        # سند شبیه‌ترین (بالاترین relevance)
        most_relevant = filtered_sources[0]
        
        st.success(f"✅ {len(filtered_sources)} سند مرتبط با ارتباط بالای {filtered_sources[-1]['relevance_score']}% پیدا شد")
        
        # بخش 1: ارجاع مستقیم به سند با نمایش میزان ارتباط
        category_class, category_text = self.get_relevance_category(most_relevant['relevance_score'])
        
        direct_reference = f"""
<div class="relevance-badge {category_class}">{category_text} - {most_relevant['relevance_score']}% تطابق</div>

📄 **سند شبیه‌ترین:**
🔢 شماره نامه: {most_relevant['شماره_نامه']}
📅 تاریخ: {most_relevant['تاریخ']}
📁 شماره پرونده: {most_relevant['شماره_پرونده']}

❓ **استعلام اصلی:**
{most_relevant['استعلام']}

💡 **پاسخ رسمی:**
{most_relevant['پاسخ']}

✍️ **پاسخ‌دهنده:** {most_relevant['پاسخ_دهنده']}
"""
        
        # بخش 2: جمع‌بندی با AI بر اساس چند سند مرتبط - IMPROVED VERSION
        # استفاده از top 3 اسناد برای context بهتر
        top_sources = filtered_sources[:3]
        
        # ساخت context غنی‌تر
        context_parts = []
        for i, src in enumerate(top_sources, 1):
            context_parts.append(f"""
=== سند {i} (میزان ارتباط: {src['relevance_score']}%) ===
شماره نامه: {src['شماره_نامه']}
تاریخ: {src['تاریخ']}
شماره پرونده: {src['شماره_پرونده']}

استعلام: {src['استعلام']}

پاسخ: {src['پاسخ']}

پاسخ‌دهنده: {src['پاسخ_دهنده']}
""")
        
        context_docs = "\n\n".join(context_parts)
        
        # پرامپت بهبود یافته با دستورالعمل‌های واضح‌تر
        prompt = f"""شما یک دستیار حقوقی خبره و دقیق هستید. وظیفه شما پاسخگویی به سوالات حقوقی بر اساس اسناد رسمی است.

📚 **اسناد مرتبط از پایگاه داده:**
{context_docs}

❓ **سوال کاربر:**
{question}

📋 **دستورالعمل‌های پاسخگویی:**
1. پاسخ شما باید **کامل و جامع** باشد (حداقل 5-8 خط)
2. از تمام اسناد مرتبط استفاده کنید و اطلاعات را **ترکیب** کنید
3. پاسخ باید به زبان **ساده و روان** باشد
4. ساختار پاسخ:
   • یک جمله مقدماتی که مستقیماً به سوال پاسخ دهد
   • توضیح جزئیات قانونی بر اساس اسناد
   • ذکر شرایط، استثناها یا نکات مهم
   • جمع‌بندی نهایی
5. اگر اسناد اطلاعات متفاوتی دارند، **همه را ذکر کنید**
6. از عبارات حقوقی و قانونی موجود در اسناد استفاده کنید
7. **هرگز** پاسخ کوتاه یا ناقص ندهید

⚖️ **پاسخ جامع:**"""

        try:
            # پیکربندی بهبود یافته برای پاسخ‌های کامل‌تر
            contents = [types.Content(
                role="user", 
                parts=[types.Part.from_text(text=prompt)]
            )]
            
            config = types.GenerateContentConfig(
                temperature=0.3,  # کمی افزایش برای پاسخ‌های طبیعی‌تر
                top_p=0.85,  # افزایش برای تنوع بیشتر
                top_k=40,  # افزایش برای انتخاب‌های بهتر
                max_output_tokens=1500,  # افزایش قابل توجه برای پاسخ‌های کامل‌تر
                candidate_count=1,
            )
            
            # نمایش پیشرفت
            summary_placeholder = st.empty()
            summary_placeholder.info("🤖 در حال تولید جمع‌بندی جامع...")
            
            summary = ""
            for chunk in self.client.models.generate_content_stream(
                model="gemini-2.0-flash-exp",  # استفاده از مدل سریع‌تر و بهتر
                contents=contents,
                config=config,
            ):
                if chunk.text:
                    summary += chunk.text
            
            # بررسی طول پاسخ
            if len(summary.strip()) < 100:
                st.warning("⚠️ پاسخ اولیه کوتاه بود، در حال تلاش مجدد...")
                
                # تلاش دوم با پرامپت ساده‌تر
                simple_prompt = f"""بر اساس این اسناد حقوقی، یک پاسخ کامل و مفصل بنویسید:

{context_docs}

سوال: {question}

لطفاً یک پاسخ حداقل 7-10 خطی بنویسید که تمام جنبه‌های سوال را پوشش دهد:"""
                
                contents = [types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=simple_prompt)]
                )]
                
                summary = ""
                for chunk in self.client.models.generate_content_stream(
                    model="gemini-2.0-flash-exp",
                    contents=contents,
                    config=config,
                ):
                    if chunk.text:
                        summary += chunk.text
            
            summary_placeholder.empty()
            
            # پاک‌سازی و فرمت‌بندی پاسخ
            summary = summary.strip()
            
            # اگر هنوز پاسخ خیلی کوتاه است
            if len(summary) < 100:
                summary = f"""بر اساس اسناد موجود:

{most_relevant['پاسخ']}

این پاسخ از سند شماره {most_relevant['شماره_نامه']} استخراج شده است. برای اطلاعات بیشتر به سند کامل مراجعه کنید."""
            
            return direct_reference, summary, filtered_sources
            
        except Exception as e:
            st.error(f"خطا در تولید جمع‌بندی: {str(e)}")
            
            # بازگشت پاسخ پیش‌فرض در صورت خطا
            fallback_summary = f"""بر اساس اسناد یافت شده:

{most_relevant['پاسخ']}

این پاسخ از مرتبط‌ترین سند (شماره {most_relevant['شماره_نامه']}) استخراج شده است."""
            
            return direct_reference, fallback_summary, filtered_sources

# برنامه اصلی
def main():
    # مقداردهی session_state
    if 'show_sources' not in st.session_state:
        st.session_state['show_sources'] = {}
    
    # هدر
    st.markdown('''
    <div class="main-header">
        <h1>⚖️ سامانه دستیار نظرات مشورتی حقوقی</h1>
        <p>🤖 جستجوی معنایی هوشمند با تکنولوژی RAG پیشرفته</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # سایدبار
    with st.sidebar:
        st.markdown("### ⚙️ اطلاعات سامانه")
        
        st.markdown('''
        <div class="info-box">
            <h4>✅ سامانه فعال</h4>
            <p>• جستجوی معنایی پیشرفته</p>
            <p>• تحلیل شباهت محتوایی</p>
            <p>• فیلتر خودکار اسناد نامرتبط</p>
            <p>• پاسخ‌های جامع و کامل</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if 'db' in st.session_state:
            count = st.session_state['db'].get_all_count()
            st.markdown(f'''
            <div class="stat-card">
                <span class="stat-number">{count}</span>
                <span class="stat-label">سند در پایگاه داده</span>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('''
        <div class="info-box">
            <h4>🎯 ویژگی‌های RAG بهبود یافته</h4>
            <p><strong>Semantic Search:</strong> جستجوی بر اساس معنا</p>
            <p><strong>Relevance Scoring:</strong> محاسبه درصد ارتباط</p>
            <p><strong>Smart Filtering:</strong> فیلتر اسناد نامرتبط</p>
            <p><strong>Complete Answers:</strong> پاسخ‌های جامع و مفصل</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # تب‌ها
    tab1, tab2, tab3 = st.tabs(["📤 بارگذاری", "💬 پرسش و پاسخ", "📊 اسناد"])
    
    # تب 1: بارگذاری
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 📤 بارگذاری اسناد")
        
        st.markdown('''
        <div class="info-box">
            <h4>📋 توضیحات</h4>
            <p>اسناد با استفاده از مدل Sentence Transformer تبدیل به embedding معنایی می‌شوند.</p>
            <p>این امکان جستجوی بر اساس معنا را فراهم می‌کند نه صرفاً کلمات.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("📁 فایل PDF:", type=['pdf'])
        
        if uploaded_file:
            if st.button("🚀 پردازش", use_container_width=True):
                with st.spinner('پردازش...'):
                    try:
                        extractor = PDFExtractor()
                        uploaded_file.seek(0)
                        text = extractor.extract_text_from_pdf(uploaded_file)
                        
                        st.success(f"✅ {len(text):,} کاراکتر استخراج شد")
                        
                        documents = extractor.parse_simple(text)
                        
                        if documents:
                            if 'db' not in st.session_state:
                                st.session_state['db'] = AdvancedLegalDatabase()
                            
                            db = st.session_state['db']
                            success = 0
                            progress = st.progress(0)
                            status = st.empty()
                            
                            for i, doc in enumerate(documents):
                                status.text(f"⚙️ در حال ایجاد embedding برای سند {i+1}...")
                                if db.add_document(doc):
                                    success += 1
                                progress.progress((i + 1) / len(documents))
                            
                            status.empty()
                            st.markdown(f'''
                            <div class="success-box">
                                <h3>✅ موفق!</h3>
                                <p>{success} سند با embedding معنایی ذخیره شد</p>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.error("❌ هیچ سندی پیدا نشد")
                    except Exception as e:
                        st.error(f"❌ خطا: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # تب 2: پرسش و پاسخ
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 💬 پرسش و پاسخ معنایی")
        
        if 'db' not in st.session_state or st.session_state['db'].get_all_count() == 0:
            st.warning("⚠️ ابتدا اسناد را بارگذاری کنید")
        else:
            st.markdown('''
            <div class="info-box">
                <h4>🎯 جستجوی هوشمند</h4>
                <p>سامانه بر اساس <strong>معنای سوال</strong> شما، مرتبط‌ترین اسناد را پیدا می‌کند.</p>
                <p>پاسخ‌ها <strong>جامع و کامل</strong> بوده و تمام جنبه‌های سوال را پوشش می‌دهند.</p>
            </div>
            ''', unsafe_allow_html=True)
            
            samples = [
                "مسئولیت امضاکنندگان چک مشترک چگونه است؟",
                "شرایط اعطای مرخصی به محکومان چیست؟",
                "صلاحیت دادگاه صلح در چه مواردی است؟",
            ]
            
            st.markdown("### 🎯 سوالات نمونه:")
            cols = st.columns(3)
            for i, q in enumerate(samples):
                with cols[i]:
                    if st.button(q, key=f"sample_{i}"):
                        st.session_state['current_question'] = q
            
            st.markdown("---")
            
            question = st.text_area(
                "✍️ سوال خود را بنویسید:",
                value=st.session_state.get('current_question', ''),
                height=100,
                placeholder="مثال: آیا دادگاه صلح می‌تواند اجراییه چک صادر کند؟"
            )
            
            if st.button("🔍 جستجو معنایی", type="primary", use_container_width=True):
                if question.strip():
                    with st.spinner('🔎 در حال تحلیل معنایی و تولید پاسخ جامع...'):
                        rag = AdvancedLegalRAG()
                        direct_ref, summary, sources = rag.generate_answer(question)
                        
                        if direct_ref and sources:
                            # نمایش سوال
                            st.markdown(f'''
                            <div class="question-card">
                                <h4>❓ سوال شما:</h4>
                                <p style="font-size: 1.2rem; line-height: 1.8;">{question}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # نمایش آمار جستجو
                            avg_relevance = sum(s['relevance_score'] for s in sources) / len(sources)
                            st.info(f"📊 تعداد اسناد مرتبط: {len(sources)} | میانگین ارتباط: {avg_relevance:.1f}%")
                            
                            # بخش 1: ارجاع مستقیم
                            st.markdown(f'''
                            <div class="answer-section">
                                <h4>📋 سند رسمی شبیه‌ترین</h4>
                                <div style="white-space: pre-wrap; line-height: 2; font-size: 1.05rem;">{direct_ref}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # بخش 2: جمع‌بندی بهبود یافته
                            if summary:
                                word_count = len(summary.split())
                                st.markdown(f'''
                                <div class="summary-section">
                                    <h4>🎯 جمع‌بندی جامع (بر اساس {len(sources[:3])} سند - {word_count} کلمه)</h4>
                                    <p style="line-height: 2.2; font-size: 1.08rem; text-align: justify;">{summary}</p>
                                </div>
                                ''', unsafe_allow_html=True)
                            
                            # بخش 3: منابع با درصد ارتباط
                            st.markdown("---")
                            st.markdown("### 📚 منابع و مستندات (مرتب شده بر اساس ارتباط)")
                            
                            for source in sources:
                                source_key = f"source_{source['index']}"
                                category_class, category_text = rag.get_relevance_category(source['relevance_score'])
                                
                                # هدر منبع با دکمه
                                col1, col2, col3 = st.columns([4, 2, 1])
                                with col1:
                                    st.markdown(f'''
                                    <div class="source-item">
                                        <strong>📌 سند {source['index']}:</strong> {source['شماره_نامه']} - {source['تاریخ']}
                                    </div>
                                    ''', unsafe_allow_html=True)
                                with col2:
                                    st.markdown(f'''
                                    <div class="relevance-badge {category_class}">
                                        {source['relevance_score']}% ارتباط
                                    </div>
                                    ''', unsafe_allow_html=True)
                                with col3:
                                    if st.button(
                                        "👁️" if not st.session_state['show_sources'].get(source_key, False) else "❌", 
                                        key=f"btn_{source_key}",
                                        help="مشاهده کامل"
                                    ):
                                        st.session_state['show_sources'][source_key] = not st.session_state['show_sources'].get(source_key, False)
                                        st.rerun()
                                
                                # محتوای کامل
                                if st.session_state['show_sources'].get(source_key, False):
                                    st.markdown(f'''
                                    <div class="document-view">
                                        <h5>📄 محتوای کامل سند شماره {source['index']}</h5>
                                        
                                        <p><strong>🔢 شماره نامه:</strong> {source['شماره_نامه']}</p>
                                        <p><strong>📅 تاریخ:</strong> {source['تاریخ']}</p>
                                        <p><strong>📁 شماره پرونده:</strong> {source['شماره_پرونده']}</p>
                                        <p><strong>📊 میزان ارتباط:</strong> {source['relevance_score']}% - {category_text}</p>
                                        
                                        <hr>
                                        
                                        <p><strong>❓ استعلام اصلی:</strong></p>
                                        <p style="background: #e3f2fd; padding: 1rem; border-radius: 8px; line-height: 2;">{source['استعلام']}</p>
                                        
                                        <hr>
                                        
                                        <p><strong>💡 پاسخ رسمی:</strong></p>
                                        <p style="background: #e8f5e9; padding: 1rem; border-radius: 8px; line-height: 2;">{source['پاسخ']}</p>
                                        
                                        <hr>
                                        
                                        <p><strong>✍️ پاسخ‌دهنده:</strong> {source['پاسخ_دهنده']}</p>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                        else:
                            st.error("❌ هیچ سند مرتبطی یافت نشد. لطفاً سوال دیگری بپرسید.")
                else:
                    st.warning("⚠️ لطفاً سوال خود را وارد کنید")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # تب 3: اسناد
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 📊 اسناد ذخیره شده")
        
        if 'db' in st.session_state and st.session_state['db'].get_all_count() > 0:
            all_docs = st.session_state['db'].collection.get()
            
            if all_docs['ids']:
                total = len(all_docs['ids'])
                st.markdown(f'''
                <div class="success-box">
                    <h3>✅ پایگاه داده فعال</h3>
                    <p>📚 {total} سند با embedding معنایی</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # جستجو
                st.markdown("### 🔍 جستجو در اسناد")
                search = st.text_input(
                    "جستجو:",
                    placeholder="شماره نامه، تاریخ یا کلمه کلیدی"
                )
                
                st.markdown("---")
                st.markdown("### 📄 لیست اسناد")
                
                displayed = 0
                for i, meta in enumerate(all_docs['metadatas'], 1):
                    if search and search.strip():
                        if not any(search.lower() in str(v).lower() for v in meta.values()):
                            continue
                    
                    displayed += 1
                    
                    with st.expander(f"📄 {i} - {meta.get('شماره_نامه')} - {meta.get('تاریخ')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**🔢 شماره نامه:** {meta.get('شماره_نامه')}")
                            st.markdown(f"**📅 تاریخ:** {meta.get('تاریخ')}")
                        
                        with col2:
                            st.markdown(f"**📁 شماره پرونده:** {meta.get('شماره_پرونده')}")
                        
                        st.markdown("---")
                        st.markdown("**❓ استعلام:**")
                        st.info(meta.get('استعلام', 'N/A'))
                        
                        st.markdown("**💡 پاسخ:**")
                        st.success(meta.get('پاسخ', 'N/A'))
                
                if search and displayed == 0:
                    st.warning("⚠️ نتیجه‌ای یافت نشد")
                
                if displayed > 0:
                    st.info(f"ℹ️ {displayed} سند نمایش داده شد")
            else:
                st.info("📭 خالی")
        else:
            st.warning("⚠️ پایگاه داده ایجاد نشده. ابتدا اسناد را بارگذاری کنید.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # فوتر
    st.markdown("---")
    st.markdown('''
    <div style="text-align: center; background: #f8f9fa; padding: 2rem; border-radius: 15px; border: 1px solid #e9ecef;">
        <p style="font-size: 1.2rem; margin-bottom: 0.5rem; color: #2c3e50;">
            <strong>⚖️ سامانه دستیار نظرات مشورتی حقوقی</strong>
        </p>
        <p style="font-size: 1rem; color: #7f8c8d;">
            🤖 RAG پیشرفته با Semantic Search و پاسخ‌های جامع
        </p>
        <p style="font-size: 0.9rem; color: #95a5a6; margin-top: 0.5rem;">
            نسخه 3.5 بهبود یافته - تکنولوژی: Gemini 2.0 Flash + ChromaDB + MPNET Embeddings
        </p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()