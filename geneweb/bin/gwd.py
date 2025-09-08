#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import http.server
import socketserver
import urllib.parse
import json
from datetime import datetime
import random

class GenewebHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.base_name = "demo"
        self.nb_persons = 1000
        self.start_date = "01/01/2024"
        self.nb_accesses = 5432
        self.nb_accesses_to_welcome = 1234
        self.version = "7.1"
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Route principale
        if parsed_url.path == "/" or parsed_url.path == "":
            if 'b' in query_params:
                self._handle_database_selection(query_params['b'][0])
            else:
                self._handle_index()
        elif parsed_url.path.startswith("/demo") or 'b' in query_params:
            self._handle_welcome(query_params)
        else:
            self._handle_404()
    
    def do_POST(self):
        self._handle_welcome({})
    
    def _handle_index(self):
        """Page de sélection de base de données - exactement comme index.txt"""
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <title>Base</title>
  <meta name="robots" content="none">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="shortcut icon" href="/images/favicon_gwd.png">
  {self._get_css()}
</head>
<body>
<div class="container text-center ">
<h1 class="mt-5">Choisir une généalogie</h1>

<div class="mt-4">
<span>Base de données :</span>

<form class="form-inline d-flex justify-content-center mt-2" method="get" action="/">
  <input type="hidden" name="lang" value="fr">
  <input name="b" placeholder="demo" class="form-control col-8">
  <button type="submit" class="btn btn-outline-secondary ml-2" value="">Ok</button>
</form>

<div class="mt-4">
Généalogies disponibles :<br>
<a href="/?b=demo">demo</a>
</div>
</div>

<h3 class="text-center mt-4">Sélection de la langue :</h3>
<div class="d-flex flex-wrap justify-content-center col-10 mx-auto">
  <a class="btn btn-outline-secondary" href="?lang=af" title="af">Afrikaans</a>
  <a class="btn btn-outline-secondary" href="?lang=ar" title="ar">العربية</a>
  <a class="btn btn-outline-secondary" href="?lang=bg" title="bg">български</a>
  <a class="btn btn-outline-secondary" href="?lang=br" title="br">brezhoneg</a>
  <a class="btn btn-outline-secondary" href="?lang=ca" title="ca">català</a>
  <a class="btn btn-outline-secondary" href="?lang=co" title="co">corsu</a>
  <a class="btn btn-outline-secondary" href="?lang=cs" title="cs">čeština</a>
  <a class="btn btn-outline-secondary" href="?lang=da" title="da">dansk</a>
  <a class="btn btn-outline-secondary" href="?lang=de" title="de">Deutsch</a>
  <a class="btn btn-outline-secondary" href="?lang=en" title="en">English</a>
  <a class="btn btn-outline-secondary" href="?lang=eo" title="eo">esperanto</a>
  <a class="btn btn-outline-secondary" href="?lang=es" title="es">Español</a>
  <a class="btn btn-outline-secondary" href="?lang=et" title="et">eesti</a>
  <a class="btn btn-outline-secondary" href="?lang=fi" title="fi">suomi</a>
  <a class="btn btn-outline-secondary" href="?lang=fr" title="fr">français</a>
  <a class="btn btn-outline-secondary" href="?lang=he" title="he">עברית </a>
  <a class="btn btn-outline-secondary" href="?lang=is" title="is">íslenska</a>
  <a class="btn btn-outline-secondary" href="?lang=it" title="it">italiano</a>
  <a class="btn btn-outline-secondary" href="?lang=lv" title="lv">Latviešu</a>
  <a class="btn btn-outline-secondary" href="?lang=lv" title="lt">Lietuvių</a>
  <a class="btn btn-outline-secondary" href="?lang=nl" title="nl">Nederlands</a>
  <a class="btn btn-outline-secondary" href="?lang=no" title="no">norsk</a>
  <a class="btn btn-outline-secondary" href="?lang=oc" title="oc">occitan</a>
  <a class="btn btn-outline-secondary" href="?lang=pl" title="pl">polski</a>
  <a class="btn btn-outline-secondary" href="?lang=pt" title="pt">Português</a>
  <a class="btn btn-outline-secondary" href="?lang=pt-br" title="pt-br">Português-do-Brasil</a>
  <a class="btn btn-outline-secondary" href="?lang=ro" title="ro">romaneste</a>
  <a class="btn btn-outline-secondary" href="?lang=ru" title="ru">русский</a>
  <a class="btn btn-outline-secondary" href="?lang=sk" title="sk">slovenčina</a>
  <a class="btn btn-outline-secondary" href="?lang=sl" title="sl">slovenščina</a>
  <a class="btn btn-outline-secondary" href="?lang=sv" title="sv">svenska</a>
  <a class="btn btn-outline-secondary" href="?lang=tr" title="tr">turkish</a>
  <a class="btn btn-outline-secondary" href="?lang=zh" title="zh">中文</a>
</div>
</div>
  <div class="btn-group float-right mt-5 mr-5">
    <span class="align-self-center">GeneWeb v. {self.version} 
    &copy; <a href="https://www.inria.fr/">INRIA</a> 1998-2017 </span>
    <a href="https://github.com/geneweb/geneweb" class="ml-1" target="_blank" title="GeneWeb sources on GitHub">
    <img src="/images/logo_bas.png" alt="Logo GeneWeb"></a>
    <a href="https://geneweb.tuxfamily.org/wiki/GeneWeb" target="_blank" title="GeneWeb documentation MediaWiki">
    <img src="/images/logo_bas_mw.png" alt="Logo GeneWeb Mediawiki"></a>
  </div>
</div>
</body>
</html>"""
        self._send_html_response(html)
    
    def _handle_database_selection(self, base_name):
        """Redirection vers la base sélectionnée"""
        self.send_response(302)
        self.send_header('Location', f'/{base_name}')
        self.end_headers()
    
    def _handle_welcome(self, query_params):
        """Page d'accueil de la base - exactement comme welcome.txt"""
        m = query_params.get('m', [''])[0]
        
        if m == 'S':
            self._handle_search(query_params)
        elif m == 'P':
            self._handle_persons_list(query_params)
        elif m == 'N':
            self._handle_surnames_list(query_params)
        elif m == 'STAT':
            self._handle_statistics()
        elif m == 'ANM':
            self._handle_anniversaries()
        elif m == 'HIST':
            self._handle_history()
        elif m == 'NOTES':
            self._handle_notes()
        elif m == 'CAL':
            self._handle_calendar()
        elif m == 'AS':
            self._handle_advanced_search()
        elif m == 'PPS':
            self._handle_places_surnames()
        elif m == 'TT':
            self._handle_titles()
        elif m == 'H' and query_params.get('v', [''])[0] == 'conf':
            self._handle_configuration()
        elif m == 'MOD_NOTES':
            self._handle_modify_notes()
        elif m == 'ADD_FAM':
            self._handle_add_family()
        else:
            self._handle_welcome_page()
    
    def _handle_welcome_page(self):
        """Page d'accueil principale - reproduction exacte de welcome.txt"""
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <title>GeneWeb – {self.base_name}</title>
  <meta name="robots" content="none">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="icon" href="/images/favicon_gwd.png">
  <link rel="apple-touch-icon" href="/images/favicon_gwd.png">
  {self._get_css()}
</head>
<body>
<div class="container" id="welcome">
{self._get_home_navigation()}

<div class="d-flex flex-column flex-md-row align-items-center justify-content-lg-around mt-1 mt-lg-3">
  <div class="col-md-3 order-2 order-md-1 align-self-center mt-3 mt-md-0">
    <div class="d-flex justify-content-center">
      <img src="/images/arbre_start.png" alt="logo GeneWeb" width="180">
    </div>
  </div>
  <div class="col-12 col-md-3 order-1 order-md-3 ml-md-2 px-0 mt-xs-2 mt-lg-0 align-self-center">
    <div class="d-flex flex-column col-md-10 pl-1 pr-0">
      <div class="btn-group btn-group-xs mt-1" role="group">
        <a href="/?b={self.base_name}&w=f" class="btn btn-sm btn-outline-primary text-nowrap" role="button">
          <i class="fas fa-user mr-2" aria-hidden="true"></i>
          Ami</a>
        <a href="/?b={self.base_name}&w=w" class="btn btn-sm btn-outline-success text-nowrap" role="button">
          <i class="fas fa-hat-wizard mr-2" aria-hidden="true"></i>
          Magicien</a>
      </div>
    </div>
  </div>
  <div class="my-0 order-3 order-md-2 flex-fill text-lg-center align-self-md-center">
    <h1 class="font-weight-bolder">Base de données {self.base_name}</h1>
    <div class="d-flex justify-content-center">
      <span class="text-center h4 font-weight-lighter">{self.nb_persons} personnes</span>
      <a class="align-self-center ml-2 mb-2" href="/?b={self.base_name}&i={random.randint(1, self.nb_persons)}" 
         data-toggle="tooltip" data-placement="bottom" title="Individu au hasard">
         <i class="fa-solid fa-dice"></i></a>
    </div>
  </div>
</div>

{self._get_search_form()}

{self._get_tools_section()}

{self._get_counter_section()}

</div>
{self._get_js()}
</body>
</html>"""
        self._send_html_response(html)
    
    def _get_home_navigation(self):
        """Navigation en haut à gauche - reproduction exacte de home.txt"""
        return f"""<div class="d-flex flex-column fix_top fix_left home-xs">
    <a tabindex="1" role="button" class="btn btn-sm btn-link p-0 border-0" href="/" title="accueil">
      <i class="fa fa-house fa-fw fa-xs" aria-hidden="true"></i>
      <i class="sr-only">accueil</i>
    </a>
    <a tabindex="3" role="button" class="btn btn-sm btn-link p-0 border-0" data-toggle="modal" data-target="#searchmodal"
      accesskey="S" title="recherche">
      <i class="fa fa-magnifying-glass fa-fw fa-xs" aria-hidden="true"></i>
      <span class="sr-only">recherche</span>
    </a>
    <a role="button" class="btn btn-sm btn-link p-0 border-0 fa-icon"
      href="/?b={self.base_name}&i={random.randint(1, self.nb_persons)}" title="Individu au hasard">
      <i class="fa fa-dice-{random.choice(['one', 'two', 'three', 'four', 'five', 'six'])} fa-fw fa-xs" aria-hidden="true"></i>
      <span class="sr-only">Individu au hasard</span>
    </a>
    <div class="btn btn-sm p-0 border-0" id="q_time">
      <i class="fa fa-hourglass-half fa-fw fa-xs p-0"></i>
    </div>
  </div>
  
  <div class="modal" id="searchmodal" role="dialog" aria-labelledby="searchpopup" aria-hidden="true">
    <div class="modal-dialog modal-lg" role="document">
      <div class="modal-content">
        <div class="modal-body" id="ModalSearch">
          <form id="collapse_search" method="get" action="/?b={self.base_name}">
            <input type="hidden" name="m" value="S">
            <div class="d-flex flex-column flex-md-row justify-content-center">
              <h3 class="rounded modal-title my-2 ml-3 ml-md-0 text-md-center w-md-50 align-self-md-center" id="searchpopup">Recherche personne</h3>
              <div class="col-12 col-md-8 mt-2 mt-md-0">
                <label class="sr-only" for="pn">Search person name</label>
                <input type="search" id="fullname" class="form-control form-control-lg no-clear-button mb-2"
                  name="pn" placeholder="Recherche personne, nom, nom public, alias ou clé"
                  autofocus tabindex="4">
                <label class="sr-only" for="n">Search public name</label>
                <input type="search" id="n" class="form-control form-control-lg no-clear-button"
                  name="n" placeholder="Nom" tabindex="5">
                <label class="sr-only" for="p">Search firstname</label>
                <input type="search" id="p" class="form-control form-control-lg no-clear-button mt-2"
                  name="p" placeholder="Prénom" tabindex="6">
                <div class="d-flex align-items-center ml-2 flex-nowrap">
                  <div class="form-check form-check-inline" data-toggle="tooltip" data-placement="bottom" title="tous">
                    <input class="form-check-input" type="checkbox" name="p_all" id="p_all" value="on">
                    <label class="form-check-label" for="p_all">tous</label>
                  </div>
                  <div class="form-check form-check-inline" data-toggle="tooltip" data-placement="bottom" title="ordre">
                    <input class="form-check-input" type="checkbox" name="p_order" id="p_order" value="on">
                    <label class="form-check-label" for="p_order">ordre</label>
                  </div>
                  <div class="form-check form-check-inline" data-toggle="tooltip" data-placement="bottom" title="exact">
                    <input class="form-check-input" type="checkbox" name="p_exact" id="p_exact" value="on">
                    <label class="form-check-label" for="p_exact">exact</label>
                  </div>
                </div>
              </div>
              <button class="btn btn-outline-primary mx-3 mx-md-0 mt-4 my-2 mt-md-0" type="submit" title="recherche">
                <i class="fa fa-magnifying-glass fa-lg mt-2 mt-md-0 mx-4 mx-md-2"></i> Recherche
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>"""
    
    def _get_search_form(self):
        """Formulaire de recherche principal - reproduction exacte"""
        return f"""<div id="welcome-search" class="d-flex flex-wrap justify-content-center mt-3 mt-lg-1">
    <div class="col col-md-10 col-xl-9">
      <form id="main-search" class="mt-2 mt-xl-4" method="get" action="/?b={self.base_name}">
        <input type="hidden" name="m" value="S" class="has_validation">
        <div class="d-flex justify-content-center">
          <div class="d-flex flex-column justify-content-center w-100">
            <div class="d-flex flex-column flex-md-row">
              <div class="w-100 w-md-auto flex-md-grow-1">
                <div class="d-flex flex-grow-1">
                  <div class="d-flex align-items-center ml-1 mr-2">
                    <abbr data-toggle="tooltip" data-placement="top" data-html="true"
                       title="Format de recherche">
                      <i class="far fa-circle-question text-primary text-primary"></i>
                    </abbr>
                  </div>
                  <input type="search" id="fullname" class="form-control form-control-lg py-0 border border-top-0" autofocus tabindex="1"
                    name="pn" placeholder="Recherche personne, nom, nom public, alias, clé">
                </div>
                <div class="d-flex mt-3">
                  <div class="btn-group-vertical mr-2">
                    <a role="button" href="/?b={self.base_name}&m=P&tri=A" data-toggle="tooltip"
                      title="Prénoms, ordre alphabétique">
                      <i class="fa fa-arrow-down-a-z fa-fw"></i></a>
                    <a role="button" href="/?b={self.base_name}&m=P&tri=F" data-toggle="tooltip"
                      title="Fréquence prénoms">
                      <i class="fa fa-arrow-down-wide-short fa-fw"></i></a>
                  </div>
                  <div class="d-flex flex-grow-1">
                    <div class="flex-grow-1 align-self-center">
                      <label for="firstname" class="sr-only col-form-label">Prénoms</label>
                      <input type="search" id="firstname" class="form-control form-control-lg border-top-0"
                        name="p" placeholder="Prénoms" tabindex="2">
                    </div>
                  </div>
                </div>
                <div class="d-flex mt-2">
                  <div class="btn-group-vertical mr-2">
                    <a role="button" href="/?b={self.base_name}&m=N&tri=A" data-toggle="tooltip"
                      title="Noms, ordre alphabétique">
                      <i class="fa fa-arrow-down-a-z fa-fw"></i></a>
                    <a role="button" href="/?b={self.base_name}&m=N&tri=F" data-toggle="tooltip"
                      title="Fréquence noms">
                      <i class="fa fa-arrow-down-wide-short fa-fw"></i></a>
                  </div>
                  <div class="d-flex flex-grow-1">
                    <div class="flex-grow-1 align-self-center">
                      <label for="surname" class="sr-only col-form-label col-sm-2">Nom</label>
                      <input type="search" id="surname" class="form-control form-control-lg border border-top-0"
                        title="mots" data-toggle="tooltip"
                        name="n" placeholder="Nom" tabindex="3">
                    </div>
                  </div>
                </div>
              </div>
              <div class="d-flex flex-column align-items-center justify-content-between mt-3 mt-md-0 mx-0 mx-md-1 px-0 px-md-3 col-md-auto small">
                <div class="d-flex flex-row flex-md-column justify-content-start mb-3 mb-md-0">
                  <div class="align-self-md-start font-weight-bold mr-3 mr-md-0 mb-0 mb-md-1">Prénoms :</div>
                  <div class="d-flex flex-row flex-md-column">
                    <div class="custom-control custom-checkbox mr-3 mr-md-0 mb-md-1" data-toggle="tooltip" data-placement="top" title="pas tous">
                      <input class="custom-control-input" type="checkbox" name="p_all" id="p_all" value="off" tabindex="4">
                      <label class="custom-control-label d-flex align-items-center" for="p_all">pas tous</label>
                    </div>
                    <div class="custom-control custom-checkbox mr-3 mr-md-0 mb-md-1" data-toggle="tooltip" data-placement="top" title="ordre">
                      <input class="custom-control-input" type="checkbox" name="p_order" id="p_order" value="on" tabindex="5">
                      <label class="custom-control-label d-flex align-items-center" for="p_order">ordre</label>
                    </div>
                    <div class="custom-control custom-checkbox" data-toggle="tooltip" data-placement="top" title="pas exact">
                      <input class="custom-control-input" type="checkbox" name="p_exact" id="p_exact" value="off" tabindex="6">
                      <label class="custom-control-label d-flex align-items-center" for="p_exact">pas exact</label>
                    </div>
                  </div>
                </div>
                <button id="global-search-inline" class="btn btn-outline-primary font-weight-bolder w-100 w-md-auto py-2 mb-1"
                  type="submit" tabindex="7">
                  <i class="fa fa-magnifying-glass fa-lg fa-fw"></i>
                  Recherche
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>"""
    
    def _get_tools_section(self):
        """Section outils - reproduction exacte"""
        return f"""<div class="d-flex flex-column justify-content-start justify-content-md-center mt-4 col-12 col-md-11 col-lg-8 mx-auto">
  <div class="h4 text-md-center"><i class="fas fa-screwdriver-wrench fa-sm fa-fw text-secondary"></i>
    Outils
  </div>
  <div class="d-flex flex-wrap justify-content-md-center">
    <a role="button" class="btn btn-outline-primary" href="/?b={self.base_name}&m=NOTES">
      <i class="far fa-file-lines fa-fw mr-1" aria-hidden="true"></i>Notes de la base
    </a>
    <a role="button" class="btn btn-outline-primary" href="/?b={self.base_name}&m=STAT">
      <i class="far fa-chart-bar fa-fw mr-1" aria-hidden="true"></i>Statistiques</a>
    <a role="button" class="btn btn-outline-primary" href="/?b={self.base_name}&m=ANM">
      <i class="fa fa-cake-candles fa-fw mr-1" aria-hidden="true"></i>Anniversaires</a>
    <a role="button" class="btn btn-outline-primary" href="/?b={self.base_name}&m=HIST&k=20">
      <i class="fas fa-clock-rotate-left fa-fw mr-1" aria-hidden="true"></i>Historique</a>
    <a role="button" class="btn btn-outline-primary" href="/?b={self.base_name}&m=PPS&bi=on&ba=on&ma=on&de=on&bu=on">
      <i class="fas fa-globe fa-fw mr-1" aria-hidden="true"></i>Lieux/Noms</a>
    <a role="button" class="btn btn-outline-primary" href="/?b={self.base_name}&m=AS">
      <i class="fa fa-magnifying-glass-plus fa-fw mr-1" aria-hidden="true"></i>Recherche avancée</a>
    <a role="button" class="btn btn-outline-primary" href="/?b={self.base_name}&m=CAL">
      <i class="far fa-calendar-days fa-fw mr-1" aria-hidden="true"></i>Calendriers</a>
    <a role="button" class="btn btn-outline-success" href="/?b={self.base_name}&m=H&v=conf">
      <i class="fas fa-gear fa-fw mr-1" aria-hidden="true"></i>Configuration</a>
    <a role="button" class="btn btn-outline-success" href="/?b={self.base_name}&m=MOD_NOTES&f=new_note">
      <i class="fa fa-file-lines fa-fw mr-1" aria-hidden="true"></i>Ajouter note</a>
    <a role="button" class="btn btn-outline-success" href="/?b={self.base_name}&m=ADD_FAM">
      <i class="fas fa-user-plus fa-fw mr-1" aria-hidden="true"></i>Ajouter famille</a>
  </div>
</div>"""
    
    def _get_counter_section(self):
        """Section compteur - reproduction exacte"""
        return f"""<div class="d-flex mt-3">
  <div class="col-11 col-md-auto mx-auto">
    Il y a eu {self.nb_accesses} consultations, dont {self.nb_accesses_to_welcome} à cette page, depuis le {self.start_date}.
  </div>
</div>
<div class="btn-group float-right mt-5 mr-5">
  <span class="align-self-center">GeneWeb v. {self.version} 
  &copy; <a href="https://www.inria.fr/">INRIA</a> 1998-2017 </span>
  <a href="https://github.com/geneweb/geneweb" class="ml-1" target="_blank" title="GeneWeb sources on GitHub">
  <img src="/images/logo_bas.png" alt="Logo GeneWeb"></a>
  <a href="https://geneweb.tuxfamily.org/wiki/GeneWeb" target="_blank" title="GeneWeb documentation MediaWiki">
  <img src="/images/logo_bas_mw.png" alt="Logo GeneWeb Mediawiki"></a>
</div>"""
    
    def _get_css(self):
        """CSS exactement comme dans css.txt et css.css"""
        return """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
/* CSS exact de Geneweb */
.fix_top { position: fixed; top: 0; z-index: 1030; }
.fix_left { left: 0; }
.home-xs { padding: 5px; }
.fa-icon { color: #6c757d; }
.fa-icon:hover { color: #007bff; }
.btn-link { text-decoration: none; }
.btn-link:hover { text-decoration: none; }
.no-clear-button::-webkit-search-cancel-button { -webkit-appearance: none; }
.scrollable-lang { max-height: 300px; overflow-y: auto; }
.text-nowrap { white-space: nowrap; }
.font-weight-bolder { font-weight: 700; }
.font-weight-lighter { font-weight: 300; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
.custom-control-input:checked ~ .custom-control-label::before { background-color: #007bff; border-color: #007bff; }
.custom-control-label::before { background-color: #fff; border: 1px solid #adb5bd; }
.custom-control-label::after { background: no-repeat 50%/50% 50%; }
.custom-checkbox .custom-control-input:checked ~ .custom-control-label::after { background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8' viewBox='0 0 8 8'%3e%3cpath fill='%23fff' d='m6.564.75-3.59 3.612-1.538-1.55L0 4.26l2.974 2.99L8 2.193z'/%3e%3c/svg%3e"); }
.btn-outline-primary { color: #007bff; border-color: #007bff; }
.btn-outline-primary:hover { color: #fff; background-color: #007bff; border-color: #007bff; }
.btn-outline-success { color: #28a745; border-color: #28a745; }
.btn-outline-success:hover { color: #fff; background-color: #28a745; border-color: #28a745; }
.btn-outline-secondary { color: #6c757d; border-color: #6c757d; }
.btn-outline-secondary:hover { color: #fff; background-color: #6c757d; border-color: #6c757d; }
.alert-danger { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
.modal { position: fixed; top: 0; left: 0; z-index: 1050; display: none; width: 100%; height: 100%; overflow: hidden; outline: 0; }
.modal-dialog { position: relative; width: auto; margin: 0.5rem; pointer-events: none; }
.modal-lg { max-width: 800px; }
.modal-content { position: relative; display: flex; flex-direction: column; width: 100%; pointer-events: auto; background-color: #fff; background-clip: padding-box; border: 1px solid rgba(0,0,0,.2); border-radius: 0.3rem; outline: 0; }
.modal-body { position: relative; flex: 1 1 auto; padding: 1rem; }
.form-control { display: block; width: 100%; height: calc(1.5em + 0.75rem + 2px); padding: 0.375rem 0.75rem; font-size: 1rem; font-weight: 400; line-height: 1.5; color: #495057; background-color: #fff; background-clip: padding-box; border: 1px solid #ced4da; border-radius: 0.25rem; transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; }
.form-control-lg { height: calc(1.5em + 1rem + 2px); padding: 0.5rem 1rem; font-size: 1.25rem; border-radius: 0.3rem; }
.border-top-0 { border-top: 0 !important; }
.border-right-0 { border-right: 0 !important; }
.border-left-0 { border-left: 0 !important; }
</style>"""
    
    def _get_js(self):
        """JavaScript pour Bootstrap et fonctionnalités"""
        return """<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
    $('#global-search').click(function() {
        $('#main-search').submit();
    });
    $('#global-search-inline').click(function() {
        $('#main-search').submit();
    });
});
</script>"""
    
    # Handlers pour les différentes fonctionnalités
    def _handle_search(self, query_params):
        pn = query_params.get('pn', [''])[0]
        p = query_params.get('p', [''])[0]
        n = query_params.get('n', [''])[0]
        
        html = f"""<!DOCTYPE html>
<html><head><title>Résultats de recherche</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Résultats de recherche</h2>
<p>Recherche pour : {pn or (p + ' ' + n).strip()}</p>
<div class="alert alert-info">Fonctionnalité de recherche en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_persons_list(self, query_params):
        html = f"""<!DOCTYPE html>
<html><head><title>Liste des prénoms</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Liste des prénoms</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_surnames_list(self, query_params):
        html = f"""<!DOCTYPE html>
<html><head><title>Liste des noms</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Liste des noms</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_statistics(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Statistiques</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Statistiques de la base</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_anniversaries(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Anniversaires</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Anniversaires</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_history(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Historique</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Historique des modifications</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_notes(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Notes de la base</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Notes de la base</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_calendar(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Calendriers</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Calendriers</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_advanced_search(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Recherche avancée</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Recherche avancée</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_places_surnames(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Lieux/Noms</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Lieux et noms</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_titles(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Titres</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Titres et domaines</h2>
<div class="alert alert-info">Fonctionnalité en cours de développement</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_configuration(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Configuration</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Configuration</h2>
<div class="alert alert-warning">Accès magicien requis</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_modify_notes(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Modifier notes</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Modifier les notes</h2>
<div class="alert alert-warning">Accès magicien requis</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_add_family(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Ajouter famille</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Ajouter une famille</h2>
<div class="alert alert-warning">Accès magicien requis</div>
<a href="/?b={self.base_name}" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self._send_html_response(html)
    
    def _handle_404(self):
        html = f"""<!DOCTYPE html>
<html><head><title>Page non trouvée</title>{self._get_css()}</head>
<body><div class="container mt-4">
<h2>Page non trouvée</h2>
<div class="alert alert-danger">La page demandée n'existe pas</div>
<a href="/" class="btn btn-primary">Retour à l'accueil</a>
</div></body></html>"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _send_html_response(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

class GenewebServer:
    def __init__(self, port=2317, host='localhost'):
        self.port = port
        self.host = host
        self.httpd = None
    
    def start(self):
        try:
            self.httpd = socketserver.TCPServer((self.host, self.port), GenewebHandler)
            print(f"Serveur GeneWeb démarré sur http://{self.host}:{self.port}")
            print(f"Accédez à votre base de données : http://{self.host}:{self.port}/?b=demo")
            print("Appuyez sur Ctrl+C pour arrêter le serveur")
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
            self.stop()
        except OSError as e:
            if e.errno == 10048:  # Port déjà utilisé sur Windows
                print(f"Erreur : Le port {self.port} est déjà utilisé")
                print("Essayez avec un autre port : python gwd.py -p 2318")
            else:
                print(f"Erreur : {e}")
    
    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print("Serveur arrêté")

def main():
    parser = argparse.ArgumentParser(description='Serveur web GeneWeb')
    parser.add_argument('-p', '--port', type=int, default=2317, help='Port du serveur (défaut: 2317)')
    parser.add_argument('-a', '--addr', default='localhost', help='Adresse du serveur (défaut: localhost)')
    
    args = parser.parse_args()
    
    server = GenewebServer(port=args.port, host=args.addr)
    server.start()

if __name__ == '__main__':
    main()