<template>
  <router-view />
</template>

<script>
export default {
  data: () => ({
    drawer: null,
    model: 0,
    colors: [
      'primary',
      'secondary',
      'yellow darken-2',
      'red',
      'orange',
    ],
  }),
};
</script>

<style scoped>
.row{
  margin: 0;
}
</style>
