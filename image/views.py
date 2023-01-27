from django.shortcuts import render
from .form import ImageForm
from .dmodels import Image
from . import detect_title
import requests
from bs4 import BeautifulSoup


# Create your views here.

def index(request):
    if request.method == 'POST':
        form = ImageForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            save_img = form.save()
            book_img = f'C:/projects/mysite/static/{save_img.image}'
            try:
                title_name = detect_title.detect_book(source=book_img)
            except:
                title_name = 'no title'
            save_img.title = title_name
            save_img.save()
            obj = form.instance
            return render(request, "index.html", {"obj": obj})
    else:
        form = ImageForm()
    img = Image.objects.all()
    return render(request, "index.html", {"img": img, "form": form})

#크롤링 포함
def detail(request, image_id):
    img = Image.objects.get(id = image_id)
    title = img.title
    #책이 한 권일 때
    if title[0] != '[':
        url = f'https://search.kyobobook.co.kr/search?keyword={title}&gbCode=TOT&target=total'
        response = requests.get(url)

        try:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            #가격정보
            price = soup.select_one('#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_price > span.price').get_text()
            #리뷰정보
            review = soup.select_one('#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_bottom > a > span.review_klover_box > span.review_klover_text.font_size_xxs').get_text()
        except:
            price = None
            review = None
        return render(request, "detail.html", {"img":img, "price":price, "review":review})
    #책이 여러 권일 때
    else:
        #str을 list로 변경
        title = title.rstrip(']')
        title = title.lstrip('[')
        titles = title.split(',')
        return render(request, "books.html", {"img":img, "titles":titles})

def inform(request, book_title):
    book_title = book_title.strip()
    book_title = book_title.strip("'")
    url = f'https://search.kyobobook.co.kr/search?keyword={book_title}&gbCode=TOT&target=total'
    response = requests.get(url)

    try:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        #책 이미지
        img = soup.select_one('#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_thumb_box.size_lg > a > span > img ')
        num = img['data-kbbfn-bid']
        url = f'https://contents.kyobobook.co.kr/pdt/{num}.jpg'
        # 가격정보
        price = soup.select_one(
            '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_price > span.price').get_text()
        # 리뷰정보
        review = soup.select_one(
            '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_bottom > a > span.review_klover_box > span.review_klover_text.font_size_xxs').get_text()
    except:
        price = None
        review = None

    return render(request, "inform.html", {"url":url, "price": price, "review": review})