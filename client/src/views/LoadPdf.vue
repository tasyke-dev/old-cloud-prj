<template>
 <v-app id="inspire" >

    <v-navigation-drawer
      v-model="drawer"
      app
    >
    <div class="d-flex flex-column justify-center mx-4">

    <v-btn
    elevation="2"
    :disabled="overlay"
    @click="goBack"
    >
    Назад
    </v-btn>

    <v-file-input
      truncate-length="15"
      @change="upload"
      show-size
      ref="upd"
      >
    </v-file-input>
    <v-btn
      elevation="2"
      color="success"
      @click="post"
      :disabled="overlay || !file"
      >
       Отправить
    </v-btn>
    <div class="">

    </div>
    </div>
    </v-navigation-drawer>

    <v-app-bar app class="blue lighten-3">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>

      <v-toolbar-title >Application</v-toolbar-title>
    </v-app-bar>

    <v-main >
      <PdfView v-if="file" :pdf-file="file" v-on:myEvent="test"/>
      <div class="mx-auto" style="width: 300px;" v-else>
      <span  ><h1>Загрузите документ, в меню</h1></span>
      </div>
    </v-main>
  <v-dialog
      v-model="overlay"
      width="500"
    >

      <v-card>
        <v-card-title class="headline grey lighten-2">
          Ожидаем
        </v-card-title>

        <v-card-text>
              <v-progress-circular
              :size="70"
              :width="7"
              color="purple"
              indeterminate
            ></v-progress-circular>
          Загрузка и обработка файла.
        </v-card-text>

        <v-divider></v-divider>

      </v-card>
    </v-dialog>
  </v-app>
</template>

<script>
import axios from 'axios';
import PdfView from '../components/PdfView.vue';

export default {
  components: {
    PdfView,
  },
  data: () => ({
    drawer: null,
    model: 0,
    file: null,
    overlay: false,
  }),
  methods: {
    upload(file) {
      this.file = null;
      setTimeout(() => {
        this.file = file;
      }, 100);
    },
    test(e) {
      this.selectedPage = e;
    },
    goBack() {
      this.$router.push({ name: 'Home' });
    },
    post() {
      // if (Object.keys(this.selectedPage).length > 0)
      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('dpi', 300);
      //  formData.append('pages', Object.keys(this.selectedPage).join());
      this.overlay = true;
      axios.post('http://45.141.102.214:5000/api/pdf', formData).then(() => {
        this.overlay = false;
        this.file = null;
        this.$refs.upd.reset();
      });
      // console.log(this.selectedPage.filter(el => el != empty));
    },
  },
};
</script>

<style scoped>
.row{
  margin: 0;
}
</style>
