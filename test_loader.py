import pytest
from loader import load_excel_data
import os

CI = os.getenv("CI", False)

file_path = os.getenv("FILE_PATH", "data/stats.xlsx")

@pytest.fixture
def file():
    sheet = "Normal Οικον Βάση"
    return load_excel_data(file_path , sheet)

@pytest.mark.skipif(CI, reason="No Excel file in CI")
@pytest.mark.parametrize( "sheet" , ["Normal Οικον Βάση",
    "Normal Οικον Βάση - Crisis", 
    "Normal Οικον Βάση - COVID",
    "Normal Κοινων Βάση",
    "Normal Κοινων Βάση - Crisis",
    "Normal Κοινων Βάση - COVID"] )
def test_all(sheet):
    docs = load_excel_data(file_path , sheet)
    assert len(docs)>0 

@pytest.mark.skipif(CI, reason="No Excel file in CI")                   
def test_load(file):
    assert len(file) == 234

@pytest.mark.skipif(CI, reason="No Excel file in CI")
def test_meta(file):
    check= file[0].metadata
    assert "region" in check and "indicator" in check and "era" in check and "source" in check
    
@pytest.mark.skipif(CI, reason="No Excel file in CI")
def test_wrongpath():
    with pytest.raises( FileNotFoundError):
        load_excel_data("fake/path/that/doesnt/exist.xlsx" , "Normal Οικον Βάση" )
