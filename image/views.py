from django.shortcuts import render
from .form import ImageForm
from .dmodels import Image
from . import detect_title
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ImageSerializer


# Create your views here.

#웹애플리케이션
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
        detail_url = url
        response = requests.get(url)

        try:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # 책 이미지
            im = soup.select_one(
                '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_thumb_box.size_lg > a > span > img ')
            bid = im['data-kbbfn-bid']
            pid = im['data-kbbfn-pid']
            url = f'https://contents.kyobobook.co.kr/pdt/{bid}.jpg'

            #가격정보
            price = soup.select_one('#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_price > span.price').get_text()

            #평점정보
            score = soup.select_one('#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_bottom > a > span.review_klover_box > span.review_klover_text.font_size_xxs').get_text()

            #리뷰정보(셀레니움 사용)
            start = time.time()
            review_url = f'https://product.kyobobook.co.kr/detail/{pid}'
            driver = webdriver.Chrome()
            driver.get(review_url)

            reviews = driver.find_elements(By.CLASS_NAME, 'comment_text')
            # 리뷰 리스트 생성
            for i in range(len(reviews)):
                reviews[i] = reviews[i].text
            # 길이가 가장 긴 리뷰를 선택
            review = max(reviews, key=len)
            end = time.time()
            print(f"{end - start:.5f} sec")
        except:
            price = None
            score = None
        return render(request, "detail.html", {"img":img,"url":url, "price":price, "score":score, "review": review, "detail_url": detail_url})
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
    detail_url = url
    response = requests.get(url)

    try:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        #책 이미지
        img = soup.select_one('#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_thumb_box.size_lg > a > span > img ')
        bid = img['data-kbbfn-bid']
        pid = img['data-kbbfn-pid']
        url = f'https://contents.kyobobook.co.kr/pdt/{bid}.jpg'
        # 가격정보
        price = soup.select_one(
            '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_price > span.price').get_text()
        # 평점정보
        score = soup.select_one(
            '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_bottom > a > span.review_klover_box > span.review_klover_text.font_size_xxs').get_text()
        # 리뷰정보(셀레니움 사용)
        review_url = f'https://product.kyobobook.co.kr/detail/{pid}'
        driver = webdriver.Chrome()
        driver.get(review_url)
        reviews = driver.find_elements(By.CLASS_NAME, 'comment_text')
        # 리뷰 리스트 생성
        for i in range(len(reviews)):
            reviews[i] = reviews[i].text
        # 길이가 가장 긴 리뷰를 선택
        review = max(reviews, key=len)
    except:
        price = None
        score = None
        review = None

    return render(request, "inform.html", {"url":url, "price": price, "score": score, "review": review, "detail_url": detail_url})


#REST api

def crawl_price_score(title):   #가격, 평점 크롤링
    url = f'https://search.kyobobook.co.kr/search?keyword={title}&gbCode=TOT&target=total'
    response = requests.get(url)

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # 가격정보
    price = soup.select_one(
        '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_price > span.price').get_text().replace('\n', '')

    # 평점정보
    score = soup.select_one(
        '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_info_box > div.prod_bottom > a > span.review_klover_box > span.review_klover_text.font_size_xxs').get_text()

    return price, score

def crawl_review(title):
    url = f'https://search.kyobobook.co.kr/search?keyword={title}&gbCode=TOT&target=total'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.select_one(
                '#shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal > div.prod_thumb_box.size_lg > a > span > img ')
    pid = tag['data-kbbfn-pid']

    review_url = f'https://product.kyobobook.co.kr/detail/{pid}'
    driver = webdriver.Chrome()
    driver.get(review_url)

    reviews = driver.find_elements(By.CLASS_NAME, 'comment_text')
    # 리뷰 리스트 생성
    for i in range(len(reviews)):
        reviews[i] = reviews[i].text
    # 길이가 가장 긴 리뷰를 선택
    review = max(reviews, key=len)

    return review

class DetectAPI(APIView):
    def post(self, request, format=None):
        serializer = ImageSerializer(data=request.FILES)
        if serializer.is_valid():
            save_img = serializer.save()
            book_img = f'C:/projects/mysite/static/{save_img.image}'

            try:
                title_name = detect_title.detect_book(source=book_img)
            except:
                title_name = 'no title'
            save_img.title = title_name
            save_img.save()
            #책이 여러 권일 경우 책 list 리턴
            if type(title_name) == list:
                context = {"titles" : title_name}
                return Response(context, status=status.HTTP_201_CREATED)
            #한 권일 경우 크롤링 결과 함께리턴
            else:
                price, score = crawl_price_score(title_name)
                review = crawl_review(title_name)
                context = {"title" : title_name, "price" : price, "score" : score, "review" : review}
                return Response(context, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


