from string import punctuation
from collections import defaultdict
from abc import ABC, abstractmethod


class Counter:
    """
    Counter of items from a list of documents
    """
    def __init__(self):
        self.item_count = defaultdict(lambda: 0)

    def _update_count(self, item):
        """
        Increment the count of item by 1

        :param item: Item in question whose count needs to be incremented
        """
        self.item_count[item] = self.item_count[item] + 1

    def get_item_count(self):
        return self.item_count

    @abstractmethod
    def process_documents(self, documents):
        """
        To be implemented by each specific Counter. After processing
        document into the individual items, self._update_count(item) is
        to be called on each item.

        :param documents: list of objects across which items need
                to be counted
        """
        pass

    def get_sorted_items(self, key, reverse=False):
        items = self.item_count.items()
        return sorted(items,
                      key=key,
                      reverse=reverse)


class WordCounter(Counter):
    def _count_words_in_text(self, text):
        """
        Preprocess text and split it into words.
        Update count for each word.

        :param text: str
        """
        # lowering case
        text = text.lower()

        words = text.split()
        # removing leading and trailing punctuation
        words = [word.strip(punctuation)
                 for word in words]

        # updating word count dictionary
        for word in words:
            self._update_count(word)

    def process_documents(self, text_documents):
        """
        :param text_documents: sequence of objects that implement IHasText
        """
        for doc in text_documents:
            doc_text = doc.get_text()
            self._count_words_in_text(doc_text)

    def get_frequent_words(self, n):
        # count is the key on which to sort. if count is same, the word's alphabetical
        # order is used to sort.
        sorted_word_counts = self.get_sorted_items(key=lambda wc: (wc[1], wc[0]),
                                                   reverse=True)
        return sorted_word_counts[:n]


class HourCounter(Counter):
    def _extract_count_hour_in_datetime(self, dt):
        """
        Extracts hour from the datetime object and updates the count for it
        :param dt: L{datetime} object
        """
        hour = dt.hour
        self._update_count(hour)

    def process_documents(self, created_time_documents):
        """
        :param created_time_documents: sequence of objects that implement
                IHasCreatedTime
        """
        for doc in created_time_documents:
            created_at_time = doc.get_created_time()
            self._extract_count_hour_in_datetime(created_at_time)

    def get_most_frequent_hour(self):
        # count is the key on which to sort.
        sorted_hour_counts = self.get_sorted_items(key=lambda hc: hc[1],
                                                   reverse=True)

        # returning the first item with maximum count.
        # Does not handle duplicates
        return sorted_hour_counts[0][0]

