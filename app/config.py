from dotenv import load_dotenv
import os

load_dotenv()

AD_ACCOUNTS = {
        "team1": {
            "KRW 아이리스_겟비너스": os.getenv("TEAM1_KRW_IRIS_GETVENUS"),
            "USD 아이리스_겟비너스": os.getenv("TEAM1_USD_IRIS_GETVENUS"),
            "KRW_라이브포레스트(ampm)": os.getenv("TEAM1_KRW_LIVEFOREST_AMPM"),
            "본투비맨_마카온2(ibr2)": os.getenv("TEAM1_BORNTOBEAMAN_MACAON2"),
            "KRW_마스터벤": os.getenv("TEAM1_KRW_MASTERBEN"),
            "KRW_라이브포레스트(와이이뮤)": os.getenv("TEAM1_KRW_LIVEFOREST_YYM"),
            "USD 마카온": os.getenv("TEAM1_USD_MACAON"),
            "KRW_뮤끄(ibr2)": os.getenv("TEAM1_KRW_MUQUE_IBR2"),
            "KRW_프렌냥(ibr2)": os.getenv("TEAM1_KRW_FRENYANG_IBR2"),
            "KRW_안미다온(ibr2)": os.getenv("TEAM1_KRW_ANMIDAON_IBR2"),
            "다트너스(mobi)": os.getenv("TEAM1_DARTNERS_MOBI"),
            "비아벨로2(mobi)": os.getenv("TEAM1_VIABELLO2_MOBI")
        },
        "team2A": {
            "디다(ibr3)": os.getenv("TEAM2A_DIDA_IBR3"),
            "KRW_해피토리(ibr2)": os.getenv("TEAM2A_KRW_HAPPYTORY_IBR2"),
            "KRW_뉴티365(오라컷플러스)": os.getenv("TEAM2A_KRW_NEWTY365_ORACUT"),
            "뉴티365(am)": os.getenv("TEAM2A_NEWTY365_AM"),
            "KRW_아비토랩(ibr2)": os.getenv("TEAM2A_KRW_ABITOLAB_IBR2"),
            "KRW_해피토리(아이치카푸)": os.getenv("TEAM2A_KRW_HAPPYTORY_ICHICAPU"),
            "KRW_해피토리(ibr3)": os.getenv("TEAM2A_KRW_HAPPYTORY_IBR3")
        },
        "team2B": {
            "KRW_리베니프(ibr2)": os.getenv("TEAM2B_KRW_RIBENIF_IBR2"),
            "#꽝컨일틻_rediettcokr": os.getenv("TEAM2B_REDIET_CO_KR"),
            "KRW_리디에뜨(ibr2)": os.getenv("TEAM2B_KRW_RIDIETTE_IBR2"),
            "KRW_씨퓨리(ibr2)": os.getenv("TEAM2B_KRW_CFURY_IBR2"),
            "KRW_리베니프2(ibr2)": os.getenv("TEAM2B_KRW_RIBENIF2_IBR2"),
            "KRW_씨퓨리2(ibr2)": os.getenv("TEAM2B_KRW_CFURY2_IBR2"),
            "#꽝컨일틻_herbeautecokr그외": os.getenv("TEAM2B_HERBEAUTE_CO_KR"),
            "KRW_고헨(ibr2)": os.getenv("TEAM2B_KRW_GOHEN_IBR2"),
            "KRW_프로젝트182(ibr2)": os.getenv("TEAM2B_KRW_PROJECT182_IBR2")
        },
        "team3": {
            "#꽝컨일틻_drmonacokr": os.getenv("TEAM3_DRMONACO_KR"),
            "#꽝컨일틻_KRW 하아르": os.getenv("TEAM3_KRW_HAAR"),
            "#꽝컨1틻_researchers": os.getenv("TEAM3_RESEARCHERS"),
            "#꽝컨일틻_researchers2": os.getenv("TEAM3_RESEARCHERS2"),
            "KRW_리프비기닝kr(ibr2)": os.getenv("TEAM3_KRW_LEAFBEGINNING_KR_IBR2"),
            "리서쳐스포우먼(am)": os.getenv("TEAM3_RESEARCHERS_WOMEN_AM"),
            "KRW 아르다오(mobi)": os.getenv("TEAM3_KRW_ARDAO_MOBI"),
            "KRW_리서쳐스포우먼2(ibr2)": os.getenv("TEAM3_KRW_RESEARCHERS_WOMEN2_IBR2")
        },
        "team4": {
            "#꽝컨일틻_bedightcokr반달": os.getenv("TEAM4_BEDIGHT_CO_KR_BANDAL"),
            "#꽝컨일틻_bedightcokr그외": os.getenv("TEAM4_BEDIGHT_CO_KR_OTHER"),
            "데이배리어(mobi)": os.getenv("TEAM4_DAYBARRIER_MOBI"),
            "데이배리어(ibr3)": os.getenv("TEAM4_DAYBARRIER_IBR3"),
            "USD_건강도감": os.getenv("TEAM4_USD_GEONGANG")
        },
        "overseas": {
            "숍라인 KRW홍콩": os.getenv("OVERSEAS_SHOPLINE_KRW_HK"),
            "홍콩(mobi)": os.getenv("OVERSEAS_HK_MOBI"),
            "숍라인_대만(mobi)": os.getenv("OVERSEAS_SHOPLINE_TW_MOBI"),
            "KRW_숍라인(대만)": os.getenv("OVERSEAS_KRW_SHOPLINE_TW"),
            "쇼피 비아벨로 sg03 [쇼피 협력광고]": os.getenv("OVERSEAS_SHOPEE_VIABELLO_SG03"),
            "us_씨퓨리(mobi)": os.getenv("OVERSEAS_US_CFURY_MOBI"),
            "USA_리베니프": os.getenv("OVERSEAS_USA_RIBENIF"),
            "US_베다이트": os.getenv("OVERSEAS_US_BEDIGHT")
        }
    }