import React, { useState } from 'react';
import { Input, Button, Form, Layout, Typography, Image, Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Header, Content } = Layout;
const { Title } = Typography;

const App = () => {
  const [imageName, setImageName] = useState('');
  const [imageURL, setImageURL] = useState(null);
  const [loading, setLoading] = useState(false);

  // Loading spinner icon
  const antIcon = <LoadingOutlined style={{ fontSize: 50 }} spin />;

  const handleSubmit = async () => {
    setLoading(true);
    setImageURL(null); // Reset imageURL while loading
    try {
      const response = await axios.post('http://localhost:5000/get-image-url', {
        imageName,
      });
      setImageURL(response.data.url);
    } catch (error) {
      console.error('Error fetching image URL:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ height: '100vh', padding: '50px' }}>
      <Header style={{ color: 'white', textAlign: 'center' }}>
        <Title style={{ color: 'white' }}>FTP Image Search</Title>
      </Header>
      <Content style={{ padding: '50px', textAlign: 'center' }}>
        <Form
          onFinish={handleSubmit}
          layout="inline"
          style={{ marginBottom: '20px' }}
        >
          <Form.Item>
            <Input
              placeholder="Enter image name"
              value={imageName}
              onChange={(e) => setImageName(e.target.value)}
            />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Search Image
            </Button>
          </Form.Item>
        </Form>

        {loading ? (
          <Spin indicator={antIcon} style={{ marginTop: '20px' }} />
        ) : (
          imageURL && (
            <div style={{ marginTop: '20px' }}>
              <Image width={200} src={imageURL} alt={imageName} />
            </div>
          )
        )}
      </Content>
    </Layout>
  );
};

export default App;
