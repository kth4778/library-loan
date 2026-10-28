# 도서관 대출 시스템 — 아래 클래스를 완성하세요. (클래스·메서드 이름은 바꾸지 마세요)

BOOKS = ("B001", "B002", "B003", "B004", "B005")
LOAN_DAYS = 14
MAX_BOOKS = 3


def _is_day(day):
    # True/False 는 파이썬에서 int 의 일종이지만 날짜로 인정하지 않는다
    return type(day) is int and day >= 1


class LibraryLoan:
    def __init__(self):
        # 책 번호 -> (빌린 사람, 빌린 날)
        self._loans = {}
        # 이름 -> [가장 늦은 정지 마지막 날, [(정지 첫날, 정지 마지막 날), ...]]
        self._bans = {}
        # 리스트처럼 사전 키로 쓸 수 없는 이름은 (이름, 기록) 목록으로 따로 둔다
        self._odd_bans = []

    def _held(self, name):
        """name 이 지금 빌리고 있는 (책 번호, 반납 기한) 목록"""
        return [(b, d + LOAN_DAYS) for b, (n, d) in self._loans.items() if n == name]

    def _ban_record(self, name, create=False):
        try:
            record = self._bans.get(name)
            if record is None and create:
                record = self._bans[name] = [0, []]
            return record
        except TypeError:
            for n, record in self._odd_bans:
                if n == name:
                    return record
            if not create:
                return None
            record = [0, []]
            self._odd_bans.append((name, record))
            return record

    def _is_suspended(self, name, day):
        record = self._ban_record(name)
        # 가장 늦은 정지보다 뒤라면 기록을 훑을 필요가 없다 (연체가 많이 쌓여도 빠르게)
        if record is None or day > record[0]:
            return False
        # 정지 기간이 겹치면 구간이 이어져서 자연히 더 늦게 끝나는 쪽을 따르게 된다 (더하지 않음)
        return any(first <= day <= last for first, last in reversed(record[1]))

    def borrow(self, book_id, name, day):
        if book_id not in BOOKS:
            return False
        if not _is_day(day):
            return False
        if book_id in self._loans:
            return False
        held = self._held(name)
        if len(held) >= MAX_BOOKS:
            return False
        if any(day > due for _, due in held):
            return False
        if self._is_suspended(name, day):
            return False
        self._loans[book_id] = (name, day)
        return True

    def return_book(self, book_id, name, day):
        if book_id not in BOOKS or not _is_day(day):
            return -1
        loan = self._loans.get(book_id)
        if loan is None:
            return -1
        borrower, borrowed_day = loan
        if borrower != name or day < borrowed_day:
            return -1

        late = max(0, day - (borrowed_day + LOAN_DAYS))
        del self._loans[book_id]
        if late > 0:
            # 반납한 날부터 연체 일수만큼의 날 동안 대출 정지
            last = day + late - 1
            record = self._ban_record(name, create=True)
            record[0] = max(record[0], last)
            record[1].append((day, last))
        return late

    def get_loans(self, name):
        return sorted(self._held(name), key=lambda loan: (loan[1], loan[0]))
