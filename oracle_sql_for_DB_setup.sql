/* ============================================================
   FINANCE TRANSACTION ANALYSER – FINAL ORACLE SQL SCRIPT
   Scope:
   - Create analytics user
   - Create FACT_TRANSACTIONS in FINANCE schema
   - Enable auto TXN_ID using SEQUENCE + TRIGGER
   - Safe for Streamlit + Power BI
   ============================================================ */


/* ============================================================
   STEP 1: CREATE APPLICATION USER
   Run as SYSTEM (or SYS as SYSDBA)
   ============================================================ */

CREATE USER C##FINANCE
IDENTIFIED BY finance1234 -- any password this is sample
DEFAULT TABLESPACE USERS
TEMPORARY TABLESPACE TEMP
QUOTA UNLIMITED ON USERS
CONTAINER = ALL;

GRANT CONNECT, RESOURCE TO C##FINANCE;


/* ============================================================
   STEP 2: LOGIN AS C##FINANCE
   (UI STEP – SQL Developer)
   ------------------------------------------------------------
   Connection Name : FINANCE
   Username        : C##FINANCE
   Password        : finance1234
   Hostname        : localhost
   Port            : 1521
   Service Name    : FREE
   ============================================================ */


/* ============================================================
   STEP 3: CREATE FACT_TRANSACTIONS TABLE
   Run as C##FINANCE
   ============================================================ */

CREATE TABLE C##FINANCE.FACT_TRANSACTIONS (
    TXN_ID                NUMBER NOT NULL,
    SESSION_ID            VARCHAR2(64 BYTE) NOT NULL,
    TXN_DATE              DATE,
    TRANSACTION_REF_ID    VARCHAR2(100 BYTE),
    TRANSACTION_CODE      VARCHAR2(200 BYTE),
    TRANSACTION_METHOD    VARCHAR2(50 BYTE),
    TRANSACTION_CATEGORY  VARCHAR2(50 BYTE),
    TRANSACTION_NATURE    VARCHAR2(50 BYTE),
    COUNTERPARTY_NAME     VARCHAR2(255 BYTE),
    COUNTERPARTY_BANK_CODE VARCHAR2(20 BYTE),
    DEBIT                 NUMBER(15,2),
    CREDIT                NUMBER(15,2),
    AMOUNT                NUMBER(15,2),
    BALANCE               NUMBER(15,2),
    REMARKS               VARCHAR2(1000 BYTE),
    CREATED_AT            TIMESTAMP DEFAULT SYSTIMESTAMP
);

ALTER TABLE C##FINANCE.FACT_TRANSACTIONS
ADD CONSTRAINT PK_FACT_TRANSACTIONS PRIMARY KEY (TXN_ID);


/* ============================================================
   STEP 4: CREATE INDEXES (PERFORMANCE)
   ============================================================ */

CREATE INDEX IDX_FACT_TXN_DATE
ON C##FINANCE.FACT_TRANSACTIONS (TXN_DATE);

CREATE INDEX IDX_FACT_CATEGORY
ON C##FINANCE.FACT_TRANSACTIONS (TRANSACTION_CATEGORY);

CREATE INDEX IDX_FACT_NATURE
ON C##FINANCE.FACT_TRANSACTIONS (TRANSACTION_NATURE);

CREATE INDEX IDX_FACT_SESSION
ON C##FINANCE.FACT_TRANSACTIONS (SESSION_ID);


/* ============================================================
   STEP 5: ENABLE AUTO TXN_ID (SEQUENCE + TRIGGER)
   REQUIRED because TXN_ID is NOT IDENTITY
   ============================================================ */

CREATE SEQUENCE C##FINANCE.FACT_TXN_SEQ
START WITH 1
INCREMENT BY 1
NOCACHE;

CREATE OR REPLACE TRIGGER C##FINANCE.FACT_TXN_BI
BEFORE INSERT ON C##FINANCE.FACT_TRANSACTIONS
FOR EACH ROW
WHEN (NEW.TXN_ID IS NULL)
BEGIN
    SELECT C##FINANCE.FACT_TXN_SEQ.NEXTVAL
    INTO :NEW.TXN_ID
    FROM dual;
END;
/
-- END TRIGGER


/* ============================================================
   STEP 6: (OPTIONAL) VERIFY
   ============================================================ */

SELECT COUNT(*) FROM C##FINANCE.FACT_TRANSACTIONS;
SELECT * FROM C##FINANCE.FACT_TRANSACTIONS FETCH FIRST 5 ROWS ONLY;


/* ============================================================
   NOTES (IMPORTANT)
   ------------------------------------------------------------
   ✔ SYSTEM schema is NOT used in application or Power BI
   ✔ Streamlit inserts WITHOUT TXN_ID (handled by trigger)
   ✔ Power BI connects to C##FINANCE schema
   ✔ Safe to TRUNCATE table between reloads
   ✔ DO NOT DROP table once dashboards are built
   ============================================================ */
