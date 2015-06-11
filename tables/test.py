from db import get_db
from country_bounds import CountryBounds
from ..util import utils
from user import User
from tile import Tile
import calendar

class Test(object):
    def setup(self):
        print 'setup'
        self.teardown()
        db = get_db()
        db.metadata.create_all(db.engine)
        db.session.commit()

        CountryBounds.load_countries()

    def teardown(self):
        for tbl in reversed(get_db().metadata.sorted_tables):
            get_db().engine.execute(tbl.delete())

    def test_countries(self):
        row = get_db().session.query(CountryBounds).filter_by(name='Afghanistan')
        assert row
        item = row.first()
        assert item.ogc_fid == 1

    def get_canada(self):
        item = get_db().session.query(CountryBounds).filter_by(name='Canada').first()
        assert isinstance(item, CountryBounds)
        return item

    def test_add_user_tile_and_report(self):
        print 'test1'
        db = get_db()

        user = User()
        user.nickname = 'nick'

        tile = Tile()

        db.session.add(user)
        db.session.add(tile)
        db.session.commit()

        w = calendar.insert_or_update_week(user, tile)
        db.session.commit()
        assert True

    def test_add_tile_for_coord(self):
        tile = Tile()
        mercator_coords = utils.create_tile_geo(-79.4, 43.7)
        tile.geometry = mercator_coords
        get_db().session.add(tile)
        get_db().session.commit()

        CountryBounds.set_country_for_tile(tile)
        canada = self.get_canada()
        assert tile.country == canada

        CountryBounds.set_country_for_tile(tile, use_intersect=True)
        assert tile.country == canada

        CountryBounds.set_country_for_tile(tile, use_nearby=True)
        assert tile.country == canada
