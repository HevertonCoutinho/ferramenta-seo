import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse, urljoin

#style terminal
from colorama import Fore, Back, Style


#bibliotecas para HTML renderizado
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Bibliotecas para analise de conteúdo
import language_tool_python

def verificar_conteudo():
    
    print(Fore.BLUE +'\n-----------Analise de conteúdo...'+ Fore.RESET)
    # Verifica se existe o título da página e mostra a quantidade de caracteres
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.text.strip()
        title_length = len(title_text)
        print(f'Título encontrado com {title_length} caracteres: {title_text}')
    else:
        print('Não foi encontrado o título da página.')

    # Verifica se existe a descrição da página e mostra a quantidade de caracteres
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        desc_text = meta_desc.get('content').strip()
        desc_length = len(desc_text)
        print(f'Descrição encontrada com {desc_length} caracteres: {desc_text}')
    else:
        print('Não foi encontrada a descrição da página.')
        

def verificar_responsividade(url):
    
    # Define as resoluções de tela a serem testadas
    resolutions = [(768, 1024), (1280, 800), (1440, 900)]

    # Define o navegador a ser utilizado
    driver = webdriver.Chrome()

    # Maximiza a janela do navegador
    driver.maximize_window()

    # Define um tempo limite para o carregamento da página
    driver.set_page_load_timeout(10)

    # Navega até a URL
    driver.get(url)
    
    print(Fore.BLUE +'\n-----------Analise do tempo de carregamento...'+ Fore.RESET)
    
    # Verifica o tempo de carregamento da página
    load_time = driver.execute_script("return performance.timing.loadEventEnd - performance.timing.navigationStart;")
    if load_time > 30000:
        print("A página demorou mais de 30 segundos para carregar.")
    else:
        print("A página carregou em menos de 30 segundos.")
        
    print(Fore.BLUE +'\n----------Analise de responsivide...'+ Fore.RESET)
    # Inicializa a variável para verificar a responsividade da página
    is_responsive = True

    # Verifica a responsividade da página para cada resolução de tela
    for width, height in resolutions:
        # Define a resolução da tela
        driver.set_window_size(width, height)

        try:
            # Espera até que um elemento da página seja carregado
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))

            # Verifica se o elemento está visível na tela
            if not element.is_displayed():
                is_responsive = False
                print(f"Resolução de tela {width}x{height}: Elemento não visível na tela.")
        except:
            is_responsive = False
            print(f"Resolução de tela {width}x{height}: Nenhum elemento encontrado.")

    # Verifica se a página é responsiva
    if is_responsive:
        print("A página é responsiva.")
    else:
        print("A página não é responsiva.")
    
    # Fecha o navegador
    driver.quit()

# Define a URL do site a ser verificado
url = 'https://www.taco.com.br/'

# Realiza a requisição da página
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print('Erro ao acessar o site: ', e)
    quit()

# Analisa o HTML da página com o BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Verifica se a página foi acessada com sucesso
if response.status_code == 200:
    
    print(Fore.BLUE +'\n----------Analise de rastreabilidade...'+ Fore.RESET)
    #verifica se a página esta sendo bloqueada pelo arquivo robots.txt
    def is_blocked_by_robots_txt(url):
        robots_url = urljoin(url, "/robots.txt")
        parsed_url = urlparse(url)
        response = requests.get(robots_url)
        
        if response.status_code == 200:
            for line in response.text.split("\n"):
                if line.startswith("Disallow:"):
                    disallowed_path = line.split(":")[1].strip()
                    if disallowed_path == "/" or parsed_url.path.startswith(disallowed_path):
                        print('Bloqueada pelo robots.txt')
                        return True                  
        print('Esta página não é bloqueada pelo robots.txt')
        return False
        
    is_blocked_by_robots_txt(url)
    
    # Verifica se a página tem tag canonical e se ela é self-referecing ou não
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical is not None:
        print(f'A página tem tag canonical apontando para {canonical["href"]}.')
        if canonical['href'] == url:
            print('A tag canonical é self-referecing.')
        else:
            print('A tag canonical não é self-referecing.')
    else:
        print('A página não possui tag canonical.')

    # Verifica se a página está indexada
    if 'noindex' in soup.find('meta', attrs={'name': 'robots'}).get('content').lower():
        print('A página não está indexada')
    else:
        print('A página está indexada')

    print(Fore.BLUE +'\n----------Analise de links e dados estruturados...'+ Fore.RESET)
    # Verifica se existem dados estruturados
    structured_data_types = []
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            structured_data = json.loads(script.string)
            if '@type' in structured_data:
                structured_data_types.append(structured_data['@type'])
        except json.JSONDecodeError:
            continue

    if structured_data_types:
        print('A página contém os seguintes tipos de dados estruturados:')
        for data_type in set(structured_data_types):
            print('- ' + data_type)
    else:
        print('A página não contém dados estruturados')
        
    # Extrai todos os links da página
    links = soup.find_all('a')

    def count_unique_links(links):
        unique_links = []
        links_with_params = []

        for link in links:
            if link.get('href'):
                if link.get('href') not in unique_links:
                    unique_links.append(link.get('href'))
                if '?' in link.get('href'):
                    links_with_params.append(link.get('href'))

        unique_links_count = len(unique_links)
        links_with_params_count = len(links_with_params)

        print(f"A página possui {unique_links_count} links únicos.")
        print(f"{links_with_params_count} dos links contêm parâmetros de URL.")

        return {"unique_links": unique_links_count, "links_with_params": links_with_params_count}

    count_unique_links(links)  # Passa a variável 'links' como argumento para a função
    
else:
    print('Não foi possível acessar a página')
    
verificar_responsividade(url)
verificar_conteudo()