import os 

DATABASE_URL = os.getenv('DATABASE_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

#Flask Config
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')

YOUTUBE_TRANSCRIPTS_ERROR_MESSAGE = "Failed to fetch transcripts, pls try again later"

#Repsonse Messages
NOT_FOUND_MESSAGE = 'Not found'
SUCCESS_MESSAGE = 'Success'
INTERNAL_SERVER_ERROR_MESSAGE = 'Something went wrong'
INVALID_CREDENTIALS = 'Invalid Credentials'


DUMMY_STOCK_PRICES ="""
        1. 2025-03-26: $2,444.99
        2. 2025-03-25: $2,434.99
        3. 2025-03-24: $2,424.99
        4. 2025-03-23: $2,414.99
        5. 2025-03-22: $2,404.99
        6. 2025-03-21: $2,394.99
        7. 2025-03-20: $2,384.99
        8. 2025-03-19: $2,374.99
        9. 2025-03-18: $2,364.99
        10. 2025-03-17: $2,354.99
        11. 2025-03-16: $2,344.99
        12. 2025-03-15: $2,334.99
        13. 2025-03-14: $2,324.99
        14. 2025-03-13: $2,314.99
        15. 2025-03-12: $2,304.99
        16. 2025-03-11: $2,294.99
        17. 2025-03-10: $2,284.99
        18. 2025-03-09: $2,274.99
        19. 2025-03-08: $2,264.99
        20. 2025-03-07: $2,254.99
        21. 2025-03-06: $2,244.99
        22. 2025-03-05: $2,234.99
        23. 2025-03-04: $2,224.99
        24. 2025-03-03: $2,214.99
        25. 2025-03-02: $2,204.99
        26. 2025-02-28: $2,194.99
        27. 2025-02-27: $2,184.99
        28. 2025-02-26: $2,174.99
        29. 2025-02-25: $2,164.99
        30. 2025-02-24: $2,154.99
"""
