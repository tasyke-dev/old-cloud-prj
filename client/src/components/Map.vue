<template>
  <div v-if="mapInfo"
  style="height: 100%;
    width: 100%;">
        <div >
          <v-btn
          fab
          dark
          large
          style="z-index: 1000;"
          class="bth-left mx-2"
          color="cyan"
          @click="prev"
          >
          <v-icon dark>
            mdi-arrow-left-bold-outline
          </v-icon>
           </v-btn>
          <v-btn
          fab
          dark
          large
          style="z-index: 1000;"
          @click="next"
          class="bth-right mx-2"
          color="cyan"
          >
          <v-icon dark>
            mdi-arrow-right-bold-outline
          </v-icon>
           </v-btn>
      </div>
      <div ref="mapContainer" class="mapContainer" id="map" v-if="renderComponent"
      style="height: 100%;
    width: 100%;" >
      <div class="delete" v-if="readyRender">
        <v-btn block :key="index"  v-for="(item, index) in objectOnMap"
        @mouseover="hoverMarker(index)"
        @mouseleave="offHoverMarker(index)"
        @click="setDeleteItem(item.type, index)"
        >
        {{item.label}}
        </v-btn>

      </div>
    </div>
  <!-- <l-map :minZoom='0'
   :maxZoom='5'  :zoom="zoom" :center="center" @click="test">
    <l-tile-layer :no-wrap="true" :url="url"></l-tile-layer>
  </l-map> -->
  <v-dialog
      v-model="dialog"
      width="300"
      style="z-index: 1000;"
    >
      <v-card>
        <v-card-title class="headline grey lighten-2">
          Текст заметки
        </v-card-title>
          <v-textarea
          solo
          v-model="dialogText"
          name="input-7-4"
          label="Solo textarea"
        ></v-textarea>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="createPopupWithText"
          >
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog
      v-model="dialogImg"
      width="300"
      style="z-index: 1000;"
      accept="image/*"
    >
      <v-card>
        <v-card-title class="headline grey lighten-2">
          Фото
        </v-card-title>
             <v-file-input
             v-model="files"
    label="File input"
    filled
    prepend-icon="mdi-camera"
  ></v-file-input>
        <v-card-actions>

          <v-btn
            color="primary"
            text

            @click="postPhoto"
          >
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
      <v-dialog
      style="z-index: 1100;"
      v-model="dialogConfirm"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="text-h5">
          Удалить объект
        </v-card-title>
        <v-card-text>Вы уверены, что хотите удалить объект?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="green darken-1"
            text
            @click="dialogConfirm = false"
          >
            Нет
          </v-btn>
          <v-btn
            color="green darken-1"
            text
            @click="deleteObj()"
          >
            Да
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>

import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import L from 'leaflet';
import maptext from './PopupText.vue';
/* eslint-disable vue/no-unused-components */
export default {
  props: ['mapInfo', 'typeInstument'],
  components: {
    maptext,
  },
  data() {
    return {
      url: 'http://inspectorvitya.ru/data/2da7246cf2584195bebb3c25e570fa69/3/{z}/{x}/{y}.png',
      index: 0,
      map: null,
      tile: null,
      dialog: false,
      dialogImg: false,
      center: [25.96618600001134, -88.70914936065674],
      pointCoordinates: [],
      arrayOfPoints: [],
      arrayOfPolygons: [],
      files: [],
      lastCoord: null,
      dialogText: '',
      myIcon: null,
      renderComponent: true,
      objectOnMap: [],
      readyRender: true,
      dialogConfirm: false,
      deleteIndex: 0,
      setEvent: null,
    };
  },
  methods: {

    addPolygonPoint(event) {
      this.pointCoordinates.push(event.latlng);
      const point = L.circle(event.latlng, {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 1,
        radius: 1,
      });
      this.arrayOfPoints.push(point);
      point.addTo(this.map);
    },
    drawPolygon() {
      const color = this.generateColor();

      const polygon = L.polygon(this.pointCoordinates, { color });
      this.arrayOfPolygons.push(polygon);
      const cords = this.coordsToArray(this.pointCoordinates);
      polygon.addTo(this.map);
      // polygon.bindPopup(`Полигон №${this.arrayOfPolygons.length}`);
      this.removePoints();
      // eslint-disable-next-line no-underscore-dangle
      const id = this.mapInfo._id.$oid;

      axios.post('http://45.141.102.214:5000/api/polygons', {
        id,
        pageNumber: this.mapInfo.images[this.index].pageNumber,
        color,
        coords: cords,
        text: 'polygon',
      }).then((res) => {
        this.mapInfo.images = res.data;
        this.map.remove();
        this.start();
      });
    },
    removePoints() {
      // eslint-disable-next-line no-plusplus
      for (let index = 0; index < this.arrayOfPoints.length; index++) {
        this.map.removeLayer(this.arrayOfPoints[index]);
      }
      this.arrayOfPoints = [];
      this.pointCoordinates = [];
    },
    coordsToArray(coords) {
      const arr = [];
      // eslint-disable-next-line no-plusplus
      for (let i = 0; i < coords.length; i++) {
        arr.push([coords[i].lat, coords[i].lng]);
      }
      return arr;
    },
    generateColor() {
      const r = Math.floor(Math.random() * 255);
      const g = Math.floor(Math.random() * 255);
      const b = Math.floor(Math.random() * 255);
      return `rgb(${r} ,${g},${b})`;
    },
    refresh() {
      // Сначала скроем компонент
      this.renderComponent = false;

      this.$nextTick(() => {
        // А потом покажем снова
        this.renderComponent = true;
      });
    },
    ctrClick(event) {
      this.addPolygonPoint(event);
    },
    hoverMarker(index) {
      if (this.objectOnMap[index].type > 0) {
        this.objectOnMap[index].obj.setIcon(L.icon({
          iconUrl: 'http://inspectorvitya.ru/data/icons/marker-icon3.png',
          iconSize: [35, 40],
        }));
      }
    },
    offHoverMarker(index) {
      if (this.objectOnMap[index].type > 0) {
        this.objectOnMap[index].obj.setIcon(L.icon({
          iconUrl: 'http://inspectorvitya.ru/data/icons/marker-icon.png',
          iconSize: [35, 40],
        }));
      }
    },
    next() {
      // eslint-disable-next-line eqeqeq
      if (this.mapInfo.images.length - 1 == this.index) { this.index = 0; } else
      if (this.mapInfo.images.length - 1 > this.index) { this.index += 1; }

      this.url = `http://inspectorvitya.ru/data/${this.mapInfo.folderName.split('/')[3]}/${this.mapInfo.images[this.index].path.split('/')[4]}/{z}/{x}/{y}.png`;
      this.map.remove();
      this.start();
    },
    prev() {
      // eslint-disable-next-line eqeqeq
      if (this.index == 0)
      // eslint-disable-next-line brace-style
      { this.index = this.mapInfo.images.length - 1; } else { this.index -= 1; }
      this.url = `http://inspectorvitya.ru/data/${this.mapInfo.folderName.split('/')[3]}/${this.mapInfo.images[this.index].path.split('/')[4]}/{z}/{x}/{y}.png`;
      this.map.remove();
      this.start();
    },
    addMarkerWithText(event) {
      this.lastCoord = event.latlng;
      this.dialog = true;
    },
    createPopupWithText() {
      // eslint-disable-next-line no-underscore-dangle
      const id = this.mapInfo._id.$oid;
      axios.post('http://45.141.102.214:5000/api/notes', {
        id,
        text: this.dialogText,
        pageNumber: this.mapInfo.images[this.index].pageNumber,
        coords: [this.lastCoord.lat, this.lastCoord.lng],
      }).then((res) => {
        this.mapInfo.images = res.data;
        this.map.remove();
        this.start();
      });
      this.dialog = false;
      this.lastCoord = null;
      this.dialogText = null;
    },
    addImage(event) {
      this.lastCoord = event.latlng;
      this.dialogImg = true;
    },
    postPhoto() {
      // eslint-disable-next-line no-underscore-dangle
      const id = this.mapInfo._id.$oid;
      const formData = new FormData();
      formData.append('file', this.files);
      formData.append('id', id);
      formData.append('pageNumber', this.mapInfo.images[this.index].pageNumber);
      formData.append('coords', `[${this.lastCoord.lat},${this.lastCoord.lng}]`);
      axios.post('http://45.141.102.214:5000/api/photonotes', formData).then((res) => {
        this.mapInfo.images = res.data;
        this.map.remove();
        this.start();
      });
      // this.$emit('updMap');
      this.dialogImg = false;
    },
    start() {
      this.readyRender = false;
      this.objectOnMap = [];
      this.map = L.map(this.$refs.mapContainer, {
        doubleClickZoom: false,
      }).setView(this.center, 0);
      this.tile = L.tileLayer(
        this.url,
        {
          minZoom: 0, maxZoom: Number(this.mapInfo.images[0].maxZoom), noWrap: true, attribution: 'Памогите',
        },
      );
      this.tile.addTo(this.map);
      this.myIcon = L.icon({
        iconUrl: 'http://inspectorvitya.ru/data/icons/marker-icon.png',
        iconSize: [35, 40],

      });
      console.log(this.mapInfo.images[this.index]);
      if (this.mapInfo.images[this.index].polygons.length > 0) {
        let i = 1;
        this.mapInfo.images[this.index].polygons.forEach((el) => {
          const obj = L.polygon(el.coords, { color: el.color }).bindTooltip(`Полигон №${i}`).openTooltip().addTo(this.map);

          this.objectOnMap.push({
            type: 0,
            color: el.color,
            coords: el.coords,
            obj,
            label: `Полигон №${i}`,
          });
          // eslint-disable-next-line no-plusplus
          i++;
        });
      }
      if (this.mapInfo.images[this.index].notes.length > 0) {
        let i = 1;
        this.mapInfo.images[this.index].notes.forEach((el) => {
          const obj = L.marker(el.coords, {
            icon: this.myIcon,
          }).addTo(this.map).bindPopup(el.text.replace('\n', '<br>'));
          this.objectOnMap.push({
            obj,
            type: 1,
            text: el.text,
            coords: el.coords,
            label: `Заметка №${i}`,
          });
          // eslint-disable-next-line no-plusplus
          i++;
        });
      }

      if (this.mapInfo.images[this.index].photoNotes.length > 0) {
        let i = 1;
        this.mapInfo.images[this.index].photoNotes.forEach((el) => {
          const marker = L.marker(el.coords, {
            icon: this.myIcon,
          }).addTo(this.map);
          marker.bindPopup(`<img src="http://inspectorvitya.ru/${el.path.slice(6)}" height="150px" width="150px"/>`);
          this.objectOnMap.push({
            obj: marker,
            type: 2,
            photo: el.path,
            label: `Фото №${i}`,
          });
          // eslint-disable-next-line no-plusplus
          i++;
        });
      }
      if (this.objectOnMap.length > 0) this.readyRender = true;
      this.setUpEvent();
    },
    setDeleteItem(type, id) {
      this.dialogConfirm = true;
      this.objDelete = {
        type, id,
      };
    },
    deleteObj() {
      let index = -1;
      const { type, id } = this.objDelete;
      console.log(id);
      switch (type) {
        case 0:
          index = this.mapInfo.images[this.index].polygons.findIndex((el) => {
            if (el.coords !== this.objectOnMap[id].coords) return false;
            return true;
          });
          this.mapInfo.images[this.index].polygons.splice(index, 1);
          break;
        case 1:
          index = this.mapInfo.images[this.index].notes.findIndex((el) => {
            if (el.coords !== this.objectOnMap[id].coords) return false;
            return true;
          });

          this.mapInfo.images[this.index].notes.splice(index, 1);
          break;
        case 2:
          console.log(this.mapInfo.images[this.index].photoNotes);
          index = this.mapInfo.images[this.index].photoNotes.findIndex((el) => {
            console.log(this.objectOnMap[id].photo);
            if (el.path !== this.objectOnMap[id].photo) return false;
            return true;
          });
          this.mapInfo.images[this.index].photoNotes.splice(index, 1);
          break;
        default:
          break;
      }
      axios.put('http://45.141.102.214:5000/api/update', this.mapInfo).then((res) => {
        this.mapInfo.images = res.data;
        this.dialogConfirm = false;
        this.map.remove();
        this.start();
      });
    },
    setUpEvent() {
      this.map.off('click', this.ctrClick);
      this.map.off('dblclick', this.drawPolygon);
      this.map.off('click', this.addMarkerWithText);
      this.map.off('click', this.addImage);
      document.getElementById('map').style.cursor = 'grab';
      switch (this.setEvent) {
        case '0':
          break;
        case '1':
          document.getElementById('map').style.cursor = 'pointer';
          this.map.on('click', this.ctrClick);
          this.map.on('dblclick', this.drawPolygon);
          break;
        case '2':
          this.map.on('click', this.addMarkerWithText);
          break;
        case '3':
          this.map.on('click', this.addImage);
          break;
        default:
          break;
      }
    },
  },
  watch: {
    typeInstument(val) {
      this.setEvent = val;
      this.map.off('click', this.ctrClick);
      this.map.off('dblclick', this.drawPolygon);
      this.map.off('click', this.addMarkerWithText);
      this.map.off('click', this.addImage);
      document.getElementById('map').style.cursor = 'grab';
      switch (val) {
        case '0':
          break;
        case '1':
          document.getElementById('map').style.cursor = 'pointer';
          this.map.on('click', this.ctrClick);
          this.map.on('dblclick', this.drawPolygon);
          break;
        case '2':
          this.map.on('click', this.addMarkerWithText);
          break;
        case '3':
          this.map.on('click', this.addImage);
          break;
        default:
          break;
      }
    },
    mapInfo() {
      this.index = 0;
      this.url = `http://inspectorvitya.ru/data/${this.mapInfo.folderName.split('/')[3]}/${this.mapInfo.images[0].path.split('/')[4]}/{z}/{x}/{y}.png`;
      this.map.remove();
      this.start();
    },
  },
  mounted() {
    console.log(this.mapInfo.images[this.index]);

    this.url = `http://inspectorvitya.ru/data/${this.mapInfo.folderName.split('/')[3]}/${this.mapInfo.images[0].path.split('/')[4]}/{z}/{x}/{y}.png`;
    this.map = L.map(this.$refs.mapContainer, {
      doubleClickZoom: false,
    }).setView(this.center, 0);
    this.tile = L.tileLayer(
      this.url,
      {
        minZoom: 0, maxZoom: Number(this.mapInfo.images[0].maxZoom), noWrap: true, attribution: 'Памогите',
      },
    );
    this.tile.addTo(this.map);
    this.index = 0;
    this.myIcon = L.icon({
      iconUrl: 'http://inspectorvitya.ru/data/icons/marker-icon.png',
      iconSize: [35, 40],
    });

    if (this.mapInfo.images[this.index].polygons.length > 0) {
      let i = 1;
      this.mapInfo.images[this.index].polygons.forEach((el) => {
        const obj = L.polygon(el.coords, { color: el.color }).bindTooltip(`Полигон №${i}`).openTooltip().addTo(this.map);

        this.objectOnMap.push({
          type: 0,
          color: el.color,
          coords: el.coords,
          obj,
          label: `Полигон №${i}`,
        });
        // eslint-disable-next-line no-plusplus
        i++;
      });
    }
    if (this.mapInfo.images[this.index].notes.length > 0) {
      let i = 1;
      this.mapInfo.images[this.index].notes.forEach((el) => {
        const obj = L.marker(el.coords, {
          icon: this.myIcon,
        }).addTo(this.map).bindPopup(el.text.replace('\n', '<br>'));
        this.objectOnMap.push({
          obj,
          type: 1,
          text: el.text,
          coords: el.coords,
          label: `Заметка №${i}`,
        });
        // eslint-disable-next-line no-plusplus
        i++;
      });
    }

    if (this.mapInfo.images[this.index].photoNotes.length > 0) {
      let i = 1;
      this.mapInfo.images[this.index].photoNotes.forEach((el) => {
        const marker = L.marker(el.coords, {
          icon: this.myIcon,
        }).addTo(this.map);
        marker.bindPopup(`<img src="http://inspectorvitya.ru/${el.path.slice(6)}" height="150px" width="150px"/>`);
        this.objectOnMap.push({
          obj: marker,
          type: 2,
          photo: el.path,
          label: `Фото №${i}`,
        });
        // eslint-disable-next-line no-plusplus
        i++;
      });
    }
    if (this.objectOnMap.length > 0) this.readyRender = true;
  },
  created() {
  },
  beforeUpdate() {

  },
};
</script>

<style scoped>
.bth-left {
   position: absolute;
   top: 50%;
   z-index: 100;
}
.bth-right {
   position: absolute;
   top: 50%;
   right: 0;
   z-index: 1;
}
.leaflet-grab{
  color:black
}
.delete {
  overflow: scroll;
  position: absolute;
  right: 0;
  bottom: 5%;
  background: white;
  max-width: 300px;
  z-index: 1100;
  max-height: 200px;
}
</style>
<style >
</style>
