<template>
  <v-app id="inspire" >
      <v-container >
      <template v-for="i in numPages">
        <div :key="i+'d'" class="flex-row d-flex justify-center  ">
        <pdf
        :key="i"
        :src="src"
        :page="i"
        style="display: inline-block; width: 50%"
        >
        </pdf>
        <v-checkbox
        v-model="chackPages[i]"
        :key="i+'s'"
        class="align-self-center"
        :value="i"
        @change="post"
        :label="`Выбрать страницу ${i}`"
        >
        </v-checkbox>
        </div>
      </template>

    </v-container>
  </v-app>
</template>

<script>

import pdf from 'vue-pdf';

export default {
  props: ['pdfFile'],
  components: {
    // eslint-disable-next-line vue/no-unused-components
    pdf,
  },
  data: () => ({
    src: null,
    numPages: null,
    chackPages: [],
  }),
  methods: {
    test() {
      console.log(this.chackPages);
    },
    post() {
      this.$emit('myEvent', this.chackPages);
    },
  },
  mounted() {
    this.src.promise.then((pdf2) => {
      this.numPages = pdf2.numPages;
    });
  },
  created() {
    console.log('object');
    const objectURL = URL.createObjectURL(this.pdfFile);
    this.src = pdf.createLoadingTask(objectURL);
  },
};
</script>

<style scoped>

</style>
