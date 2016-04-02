from django.test import TestCase

from core.models import *


class TransactionTests(TestCase):
    def setUp(self):
        self.seller = Team.objects.create(name="Seller", members="S")
        self.buyer = Team.objects.create(name="Buyer", members="B")

        self.safe = Entity.objects.create(name="Safe entity")
        self.licence = Entity.objects.create(name="Licence")
        self.unsafe = Entity.objects.create(name="Unsafe entity", licence=self.licence)

    def test_transaction_valid(self):
        with Transaction() as t:
            t.add(self.seller, self.safe, 10)

        with Transaction() as t:
            t.remove(self.seller, self.safe, 1)

        with self.assertRaises(InvalidTransaction):
            with Transaction() as t:
                t.remove(self.seller, self.safe, 10)

    def test_licence(self):
        self.seller.get_balance(self.unsafe).set_amount(0).save()
        self.seller.get_balance(self.licence).set_amount(0).save()

        with self.assertRaises(InvalidTransaction):
            with Transaction() as t:
                t.add(self.seller, self.unsafe, 10)

        with Transaction() as t:
            t.add(self.seller, self.licence, 1)
            t.add(self.seller, self.unsafe, 10)

        with self.assertRaises(InvalidTransaction):
            with Transaction() as t:
                t.remove(self.seller, self.licence, 1)

    def test_double(self):
        self.seller.get_balance(self.safe).set_amount(0).save()

        with Transaction() as t:
            t.add(self.seller, self.safe, 10)
            t.add(self.seller, self.safe, 10)

        self.assertEqual(20, self.seller.get_balance(self.safe).amount)

    def test_exchange(self):
        self.seller.get_balance(self.licence).set_amount(1).save()
        self.seller.get_balance(self.unsafe).set_amount(1).save()
        self.buyer.get_balance(self.licence).set_amount(0).save()
        self.buyer.get_balance(self.unsafe).set_amount(0).save()

        with Transaction() as t:
            t.block(self.seller, self.licence, 1)
            t.block(self.seller, self.unsafe, 1)

        with Transaction() as t:
            t.unblock(self.seller, self.licence, 1)
            t.unblock(self.seller, self.unsafe, 1)
            t.move(self.seller, self.buyer, self.licence, 1)
            t.move(self.seller, self.buyer, self.unsafe, 1)

        self.assertEqual(0, self.seller.get_balance(self.licence).amount)
        self.assertEqual(0, self.seller.get_balance(self.unsafe).amount)
        self.assertEqual(1, self.buyer.get_balance(self.licence).amount)
        self.assertEqual(1, self.buyer.get_balance(self.unsafe).amount)

    def test_reservation(self):
        self.seller.get_balance(self.safe).set_amount(10).save()

        with Transaction() as t:
            t.needs(self.seller, self.safe, 5)
            t.remove(self.seller, self.safe, 5)

        with self.assertRaises(InvalidTransaction):
            with Transaction() as t:
                t.remove(self.seller, self.safe, 5)
                t.needs(self.seller, self.safe, 5)

    def test_phased_reservation(self):
        self.seller.get_balance(self.safe).set_amount(5).save()

        with self.assertRaises(InvalidTransaction):
            with Transaction() as t:
                t.remove(self.seller, self.safe, 5)
                t.needs(self.seller, self.safe, 5)
                t.assertValidState()
                t.add(self.seller, self.safe, 1000)



