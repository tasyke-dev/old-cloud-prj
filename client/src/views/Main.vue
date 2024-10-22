<template>
    <v-app id="inspire" >

    <v-navigation-drawer
      v-model="drawer"
      style="z-index:9999;"
      bottom
      app
    >
    <div class="d-flex flex-column justify-center mx-4">
         <v-select
            v-if="docs"
            v-model="map"
            :items="docs"
            item-text="filename"
            item-value="_id.$oid"
            label="Select"
            persistent-hint
            return-object
            single-line
            @change="test"
          ></v-select>
          <v-radio-group v-model="indexInstrument">
            <v-radio
                label="Ничего"
                value="0"
              >
            </v-radio>
                <v-radio
                label="Полигон"
                value="1"
              >
            </v-radio>

                <v-radio
                label="Заметка"
                value="2"
              >
            </v-radio>
                    <v-radio
                label="Фотка"
                value="3"
              >
            </v-radio>
    </v-radio-group>
              <router-link :to="{ name: 'LoadPdf'}">
    <v-btn
    elevation="2"
    >
    Новый документ
    </v-btn>
    </router-link>
       </div>
    </v-navigation-drawer>

    <v-app-bar app class="blue lighten-3">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title >Application</v-toolbar-title>
    </v-app-bar>
    <v-main >
        <Map :mapInfo="map" :typeInstument="indexInstrument" @updMap="test" v-if="map" />
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios';
import Map from '../components/Map.vue';

export default {
  components: {
    Map,
  },
  data: () => ({
    drawer: null,
    model: 0,
    docs: null,
    map: null,
    indexInstrument: '0',

  }),
  methods: {
    test() {

    },
  },
  created() {
    axios.get('http://45.141.102.214:5000/api').then(({ data }) => {
      data.forEach((el) => {
        el.images.sort((a, b) => Number(a.pageNumber) - Number(b.pageNumber));
      });

      this.docs = data;
    }).catch((e) => {
      console.log(e);
    });
  },
};
</script>

<style scoped>
.row{
  margin: 0;
}

</style>
